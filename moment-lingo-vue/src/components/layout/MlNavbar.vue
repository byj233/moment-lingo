<script lang="ts" setup>
import router from '@/router';

defineProps<{
  title: string;
}>();

function onLeftClick() {
  router.back();
}
</script>

<template>
  <t-navbar :title="title" class="z-[9999]" left-arrow @left-click="onLeftClick"/>
</template>
