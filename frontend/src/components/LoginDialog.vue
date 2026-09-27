<template>
  <el-dialog
    v-model="visible"
    title="欢迎来到邻里交换"
    width="380px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
  >
    <p class="tip">输入昵称即可开始，邻里之间无需密码</p>
    <el-input
      v-model="nickname"
      placeholder="例如：3号楼小李"
      maxlength="20"
      @keyup.enter="submit"
    />
    <template #footer>
      <el-button @click="visible = false">先逛逛</el-button>
      <el-button type="primary" :loading="loading" @click="submit">进入</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const visible = defineModel({ type: Boolean, default: false })
const userStore = useUserStore()
const nickname = ref('')
const loading = ref(false)

async function submit() {
  const name = nickname.value.trim()
  if (!name) {
    ElMessage.warning('请输入昵称')
    return
  }
  loading.value = true
  try {
    await userStore.login(name)
    ElMessage.success(`欢迎，${name}`)
    visible.value = false
  } catch (e) {
    ElMessage.error('登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.tip {
  margin: 0 0 12px;
  color: #888;
  font-size: 13px;
}
</style>
