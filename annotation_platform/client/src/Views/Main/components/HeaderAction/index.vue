<template>
  <div>
    <a-page-header title="记录工具" sub-title="辅助记录搜索行为">
      <template #tags>
        <a-tag :color="appStatus === APP_STATUS.OPEN ? 'green' : 'grey'">
          {{
            appStatus === APP_STATUS.OPEN ? '记录中' : '未开启'
          }}
        </a-tag>
      </template>
      <template #extra>
        <div style="display: flex; align-items: center">
          <a-input @change="onTopicInputChange" :disabled="appStatus === APP_STATUS.OPEN" :value="topicInput" class="topic-input" placeholder="输入问题编号" style="width: 180px" />
          &nbsp;&nbsp;
          <a-switch
            :checked="appStatus === APP_STATUS.OPEN"
            @click="toggleAppStatus"
          />
          &nbsp;&nbsp;
          <span>
            {{
              appStatus === APP_STATUS.OPEN ? '记录中' : '未开启记录'
            }}
          </span>
        </div>
      </template>
      <a-row type="flex">
        <a-statistic title="剩余操作步骤" :value="`${restStep} / ${maxStep}`" />
      </a-row>
      <a-divider />
    </a-page-header>
  </div>
</template>

<script lang="ts" src="./index.ts"></script>
