<template>
  <el-card class="item-card" shadow="hover" @click="$emit('click')">
    <div class="img-box">
      <el-image v-if="item.image_url" :src="item.image_url" fit="cover" class="img" />
      <div v-else class="img img-placeholder">无图</div>
      <div class="freshness"><FreshnessTag :created-at="item.created_at" /></div>
      <el-tag v-if="item.status === 'given'" type="info" class="given-tag">已送出</el-tag>
    </div>
    <div class="body">
      <div class="name">{{ item.name }}</div>
      <div class="desc">{{ item.description }}</div>
      <div class="meta">
        <span class="price" :class="{ free: item.trade_type !== 'priced' }">{{ priceText }}</span>
        <span class="want">{{ item.want_count }} 人想要</span>
      </div>
      <div class="owner">发布者：{{ item.owner_nickname }}</div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import FreshnessTag from './FreshnessTag.vue'

const props = defineProps({ item: { type: Object, required: true } })
defineEmits(['click'])

const priceText = computed(() => {
  if (props.item.trade_type === 'free') return '免费送'
  if (props.item.trade_type === 'offer') return '随便给'
  return `¥${props.item.price}`
})
</script>

<style scoped>
.item-card {
  cursor: pointer;
}
.img-box {
  position: relative;
  height: 160px;
  background: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}
.img {
  width: 100%;
  height: 100%;
  display: block;
}
.img-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
  height: 100%;
}
.freshness {
  position: absolute;
  top: 8px;
  left: 8px;
}
.given-tag {
  position: absolute;
  top: 8px;
  right: 8px;
}
.body {
  padding-top: 10px;
}
.name {
  font-weight: 600;
  font-size: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.desc {
  color: #999;
  font-size: 13px;
  margin: 6px 0;
  height: 20px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.price {
  color: #f56c6c;
  font-weight: 700;
  font-size: 16px;
}
.price.free {
  color: #67c23a;
}
.want {
  color: #999;
  font-size: 12px;
}
.owner {
  color: #bbb;
  font-size: 12px;
  margin-top: 6px;
}
</style>
