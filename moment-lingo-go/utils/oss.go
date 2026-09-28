package utils

import (
	"MomentLingo/config"
	"context"
	"fmt"
	"log/slog"
	"time"

	openapi "github.com/alibabacloud-go/darabonba-openapi/v2/client"
	sts "github.com/alibabacloud-go/sts-20150401/v2/client"
	teaUtil "github.com/alibabacloud-go/tea-utils/v2/service"
	"github.com/aliyun/alibabacloud-oss-go-sdk-v2/oss"
	"github.com/aliyun/alibabacloud-oss-go-sdk-v2/oss/credentials"
)

type ossUtil struct {
}

var Oss ossUtil

func (ossUtil) StsPutToken() H {
	val := Rdb.Get("oss:sts")
	if val != nil {
		return JSON.ToMap(*val)
	}

	policy := `{
	             "Version": "1",
	             "Statement": [
	               {
	                 "Effect": "Allow",
	                 "Action": ["oss:PutObject"],
	                 "Resource": [
	                 	"acs:oss:*:*:moment-lingo/temp/*",
	                 	"acs:oss:*:*:moment-lingo/avatar/*"
	                 ]
	               }
	             ]
	           }`

	conf := &openapi.Config{
		AccessKeyId:     new(config.Conf.AliYun.AccessKeyId),
		AccessKeySecret: new(config.Conf.AliYun.AccessKeySecret),
		RegionId:        new("cn-hangzhou"),
	}

	conf.Endpoint = new("sts.cn-hangzhou.aliyuncs.com")
	stsClient, err := sts.NewClient(conf)
	if err != nil {
		slog.Error("oss错误", "OssError", err)
		panic(fmt.Errorf("oss错误 %w", err))
	}

	request := sts.AssumeRoleRequest{
		DurationSeconds: new(int64(3600)),
		RoleArn:         new(""),
		RoleSessionName: new("oss-moment-lingo"),
		Policy:          new(policy),
	}

	resp, err := stsClient.AssumeRoleWithOptions(&request, &teaUtil.RuntimeOptions{})
	if err != nil {
		slog.Error("oss错误", "OssError", err)
		panic(fmt.Errorf("oss错误 %w", err))
	}

	cred := resp.Body.Credentials
	res := H{
		"accessKeyId":     cred.AccessKeyId,
		"accessKeySecret": cred.AccessKeySecret,
		"stsToken":        cred.SecurityToken,
	}

	Rdb.SetEx("oss:sts", JSON.Stringify(res), time.Minute*55)
	return res
}

func (ossUtil) Presign(objectName string) string {
	provider := credentials.NewStaticCredentialsProvider(config.Conf.AliYun.AccessKeyId, config.Conf.AliYun.AccessKeySecret)
	cfg := oss.LoadDefaultConfig().
		WithCredentialsProvider(provider).
		WithRegion("cn-hangzhou").
		WithEndpoint("https://oss.momentlingo.cn").
		WithUseCName(true)

	client := oss.NewClient(cfg)

	result, err := client.Presign(context.TODO(), &oss.GetObjectRequest{
		Bucket: new("moment-lingo"),
		Key:    new(objectName),
	}, oss.PresignExpires(time.Hour))

	if err != nil {
		slog.Error("oss生成预览URL错误", "OssError", err)
		panic(fmt.Errorf("oss生成预览URL错误 %w", err))
	}

	return result.URL
}

func (ossUtil) PublicReadAcl(objectName string) {
	provider := credentials.NewStaticCredentialsProvider(config.Conf.AliYun.AccessKeyId, config.Conf.AliYun.AccessKeySecret)
	cfg := oss.LoadDefaultConfig().
		WithCredentialsProvider(provider).
		WithRegion("cn-hangzhou").
		WithEndpoint("https://oss.momentlingo.cn").
		WithUseCName(true)

	client := oss.NewClient(cfg)

	// 创建设置对象ACL的请求
	putRequest := &oss.PutObjectAclRequest{
		Bucket: new("moment-lingo"),
		Key:    new(objectName),
		Acl:    oss.ObjectACLPublicRead,
	}

	_, err := client.PutObjectAcl(context.TODO(), putRequest)
	if err != nil {
		slog.Error("oss设置对象ACL错误", "OssError", err)
		panic(fmt.Errorf("oss设置对象ACL错误 %w", err))
	}
}

func (ossUtil) BuildUrl(objectName string) string {
	return fmt.Sprintf("https://oss.momentlingo.cn/%s", objectName)
}
