<template>
  <div class="mine">
    <el-empty v-if="!userStore.isLoggedIn" description="请先登录" />

    <el-tabs v-else v-model="tab">
      <el-tab-pane label="我的发布" name="items">
        <div v-loading="loadingItems" class="grid">
          <ItemCard
            v-for="it in myItems"
            :key="it.id"
            :item="it"
            @click="$router.push(`/item/${it.id}`)"
          />
          <el-empty v-if="!loadingItems && myItems.length === 0" description="还没有发布过物品" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="我想要的" name="wants">
        <div v-loading="loadingWants" class="want-list">
          <div
            v-for="w in myWants"
            :key="w.id"
            class="want-item"
            @click="$router.push(`/item/${w.item_id}`)"
          >
            <el-image v-if="w.item_image" :src="w.item_image" fit="cover" class="thumb" />
            <div v-else class="thumb thumb-ph">无图</div>
            <div class="w-info">
              <div class="w-name">{{ w.item_name }}</div>
              <div class="w-meta">{{ priceText(w) }}</div>
            </div>
            <el-tag v-if="w.item_status === 'given'" type="info">已送出</el-tag>
            <el-tag v-else-if="w.status === 'confirmed'" type="success">已成交</el-tag>
            <el-tag v-else type="warning">想要中</el-tag>
          </div>
          <el-empty v-if="!loadingWants && myWants.length === 0" description="还没有想要的物品" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { useUserStore } from '../stores/user'
import ItemCard from '../components/ItemCard.vue'

const userStore = useUserStore()
const tab = ref('items')
const myItems = ref([])
const myWants = ref([])
const loadingItems = ref(false)
const loadingWants = ref(false)

function priceText(w) {
  if (w.item_trade_type === 'free') return '免费送'
  if (w.item_trade_type === 'offer') return '随便给'
  return `¥${w.item_price}`
}

async function loadItems() {
  loadingItems.value = true
  try {
    const { data } = await api.get('/me/items')
    myItems.value = data
  } finally {
    loadingItems.value = false
  }
}

async function loadWants() {
  loadingWants.value = true
  try {
    const { data } = await api.get('/me/wants')
    myWants.value = data
  } finally {
    loadingWants.value = false
  }
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    loadItems()
    loadWants()
  }
})
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  min-height: 120px;
}
.want-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 120px;
}
.want-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
}
.thumb {
  width: 56px;
  height: 56px;
  border-radius: 4px;
  flex-shrink: 0;
}
.thumb-ph {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #bbb;
  font-size: 12px;
}
.w-info {
  flex: 1;
}
.w-name {
  font-weight: 600;
}
.w-meta {
  color: #999;
  font-size: 13px;
  margin-top: 4px;
}
</style>
