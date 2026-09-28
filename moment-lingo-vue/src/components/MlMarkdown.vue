<script lang="ts" setup>
import MarkdownRender, { MarkdownCodeBlockNode, setCustomComponents } from 'markstream-vue';

defineProps<{
  content: string;
}>();

setCustomComponents({
  code_block: MarkdownCodeBlockNode
});
</script>

<template>
  <markdown-render :content="content"/>
</template>