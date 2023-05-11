import { defineComponent, ref } from 'vue';
import { APP_STATUS } from '../../interface';
import { message } from 'ant-design-vue';
import $ from 'jquery';

export default defineComponent({
  props: ['maxStep', 'restStep', 'appStatus'],
  setup(props, context) {
    const { emit } = context;

    const topicInput = ref('');

    const toggleAppStatus = () => {
      if (!topicInput.value) {
        message.warn('请输入问题编号');
        return false;
      }
      emit('toggleAppStatus');
    };

    const onTopicInputChange = (e: any) => {
      topicInput.value = e.target.value;
    };

    // @ts-ignore
    window.__setTopic = (val) => {
      topicInput.value = val;
    };

    // @ts-ignore
    window.__getTopic = () => {
      return topicInput.value;
    };

    return {
      toggleAppStatus,
      APP_STATUS,
      topicInput,
      onTopicInputChange,
    };
  },
});
