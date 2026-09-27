<template>
  <el-tag :type="tagType" size="small" effect="light">{{ label }}</el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ createdAt: { type: String, required: true } })

const hours = computed(() => {
  const created = new Date(props.createdAt).getTime()
  return (Date.now() - created) / 3600000
})

const label = computed(() => {
  if (hours.value < 24) return '刚上架'
  if (hours.value < 72) return '新上架'
  return `已上架${Math.floor(hours.value / 24)}天`
})

const tagType = computed(() => {
  if (hours.value < 24) return 'danger'
  if (hours.value < 72) return 'warning'
  return 'info'
})
</script>
