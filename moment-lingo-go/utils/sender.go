package utils

import (
	"MomentLingo/config"
	"bytes"
	"fmt"
	"html/template"
	"log/slog"

	"github.com/go-resty/resty/v2"
	"gopkg.in/gomail.v2"
)

func SendCaptchaEmail(to, code string) {
	html := `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>账户验证码</title>
    <style type="text/css">
        body {
            margin: 0;
            padding: 20px 0;
            min-width: 100%;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #333;
            background-color: #f7f9fc;
        }
       
        .email-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 30px 25px;
            background-color: #fff;
            border-radius: 6px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        }
       
        h1 {
            margin: 0 0 20px;
            font-size: 20px;
            color: #2d4bcc;
            text-align: center;
        }
       
        .content p {
            margin: 10px 0;
            font-size: 15px;
            line-height: 1.6;
            color: #555;
        }
        
        .code-box {
            margin: 20px auto;
            width: fit-content;
            padding: 12px 20px;
            background-color: #f7f9fc;
            border-radius: 4px;
            font-family: "Courier New", Courier, monospace;
            font-size: 26px;
            font-weight: 700;
            color: #2d4bcc;
            letter-spacing: 6px;
        }
     
        .code-note {
            text-align: center;
            font-size: 13px;
            color: #777;
            margin: 5px 0 20px;
        }
    
        @media only screen and (max-width: 480px) {
            .email-container {
                padding: 20px 15px;
                border-radius: 0;
                box-shadow: none;
            }
            .code-box {
                font-size: 22px;
                padding: 10px 15px;
                letter-spacing: 4px;
            }
        }
    </style>
</head>
<body>
    <table class="email-container" align="center" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
            <td>
                <h1>账户验证</h1>
                <div class="content">
                    <p>您好，</p>
                    <p>请使用以下验证码完成账户验证：</p>
                    <div class="code-box">{{.code}}</div>
                    <p class="code-note">验证码有效期 5 分钟，过期请重新获取</p>
                    <p>如有疑问，可联系客服：</p>
                </div>
            </td>
        </tr>
    </table>
</body>
</html>
`

	tpl, err := template.New("email").Parse(html)
	if err != nil {
		slog.Error("发送邮件失败", "EmailError", err)
		panic(fmt.Errorf("发送邮件失败 %w", err))
	}

	data := H{
		"code": code,
	}

	var buf bytes.Buffer
	err = tpl.Execute(&buf, data)
	if err != nil {
		slog.Error("发送邮件失败", "EmailError", err)
		panic(fmt.Errorf("发送邮件失败 %w", err))
	}

	m := gomail.NewMessage()
	m.SetHeader("From", m.FormatAddress(config.Conf.Email.Username, "MomentLingo"))
	m.SetHeader("To", to)
	m.SetHeader("Subject", "验证码")
	m.SetBody("text/html", buf.String())

	d := gomail.NewDialer(config.Conf.Email.Host, config.Conf.Email.Port, config.Conf.Email.Username, config.Conf.Email.Password)

	if err := d.DialAndSend(m); err != nil {
		slog.Error("发送邮件失败", "EmailError", err)
		panic(fmt.Errorf("发送邮件失败 %w", err))
	}
}

func SendCaptchaMessage(phone, code string) {
	client := resty.New()

	resp, err := client.R().SetBody(H{
		"phone": phone,
		"code":  code,
	}).Post(fmt.Sprintf("%s/sms", config.Conf.Python.Url))

	if err != nil {
		slog.Error("发送短信失败", "SmsError", err)
		panic(fmt.Errorf("发送短信失败 %w", err))
	}

	r := Resp.BuildWithRestyResp(resp)
	if r.Code != 200 {
		slog.Error("发送短信失败", "SmsError", err)
		panic(fmt.Errorf("发送短信失败 %w", err))
	}
}
