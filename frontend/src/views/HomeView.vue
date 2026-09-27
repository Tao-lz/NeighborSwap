<template>
  <div class="home">
    <div class="toolbar">
      <el-input
        v-model="q"
        placeholder="搜索名称或描述"
        clearable
        class="search"
        @keyup.enter="fetchItems"
        @clear="fetchItems"
      >
        <template #append>
          <el-button @click="fetchItems">搜索</el-button>
        </template>
      </el-input>
      <el-radio-group v-model="tradeType" @change="fetchItems">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="free">免费</el-radio-button>
        <el-radio-button value="priced">标价</el-radio-button>
      </el-radio-group>
    </div>

    <div v-loading="loading" class="grid">
      <ItemCard
        v-for="item in items"
        :key="item.id"
        :item="item"
        @click="$router.push(`/item/${item.id}`)"
      />
      <el-empty
        v-if="!loading && items.length === 0"
        description="暂时没有在售物品，来发布第一件吧"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import ItemCard from '../components/ItemCard.vue'

const q = ref('')
const tradeType = ref('all')
const items = ref([])
const loading = ref(false)

const typeMap = { all: undefined, free: 'free,offer', priced: 'priced' }

async function fetchItems() {
  loading.value = true
  try {
    const { data } = await api.get('/items', {
      params: {
        q: q.value || undefined,
        trade_type: typeMap[tradeType.value],
        status: 'available',
      },
    })
    items.value = data
  } finally {
    loading.value = false
  }
}

onMounted(fetchItems)
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}
.search {
  max-width: 360px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
  min-height: 200px;
}
</style>
