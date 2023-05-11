<template>
  <div>
    <div class="bg"></div>
    <Main />
  </div>
</template>

<script setup lang="ts">
import Main from '@/Views/Main/index.vue';
</script>

<style>
.ant-list-item {
  padding-left: 16px !important;
}

.bg {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  top: 0;
  background-image: url(https://gw.alipayobjects.com/zos/rmsportal/TVYTbAXWheQpRcWDaDMu.svg);
  background-repeat: no-repeat;
  background-position: center 110px;
  background-size: 100%;
  z-index: -1;
  filter: blur(4px);
}

.__find-item {
  background: #cb4b4b;
  color: white;
}

.__find-item-active {
  background: red;
  box-shadow: 0 0 10px red;
  color: white;
}
</style>
