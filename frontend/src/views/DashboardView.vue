<template>
  <div v-loading="loading" class="dash">
    <div class="stats">
      <el-card class="stat">
        <div class="stat-num">{{ data.month_published }}</div>
        <div class="stat-label">本月发布</div>
      </el-card>
      <el-card class="stat">
        <div class="stat-num">{{ data.month_given }}</div>
        <div class="stat-label">本月成交</div>
      </el-card>
      <el-card class="stat">
        <div class="stat-num">{{ data.current_available }}</div>
        <div class="stat-label">当前在售</div>
      </el-card>
    </div>

    <div class="highlights">
      <el-card class="hl">
        <template #header>最快被领走的物品</template>
        <div v-if="data.fastest_given">
          <div class="hl-name">{{ data.fastest_given.name }}</div>
          <div class="hl-sub">上架 {{ duration(data.fastest_given) }} 后被领走</div>
        </div>
        <el-empty v-else description="暂无成交记录" :image-size="60" />
      </el-card>

      <el-card class="hl">
        <template #header>最多人想要（尚未成交）</template>
        <div v-if="data.hottest_wanted">
          <div class="hl-name">{{ data.hottest_wanted.name }}</div>
          <div class="hl-sub">{{ data.hottest_wanted.want_count }} 人想要</div>
        </div>
        <el-empty v-else description="暂无在售物品" :image-size="60" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const data = ref({
  month_published: 0,
  month_given: 0,
  current_available: 0,
  fastest_given: null,
  hottest_wanted: null,
})
const loading = ref(false)

function duration(item) {
  const created = new Date(item.created_at).getTime()
  const given = new Date(item.given_at).getTime()
  const mins = Math.floor((given - created) / 60000)
  if (mins < 60) return `${mins} 分钟`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时`
  return `${Math.floor(hours / 24)} 天`
}

async function load() {
  loading.value = true
  try {
    const { data: d } = await api.get('/dashboard')
    data.value = d
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.stat {
  text-align: center;
}
.stat-num {
  font-size: 36px;
  font-weight: 700;
  color: #409eff;
}
.stat-label {
  color: #999;
  margin-top: 8px;
}
.highlights {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.hl-name {
  font-weight: 600;
  font-size: 18px;
}
.hl-sub {
  color: #999;
  margin-top: 8px;
}
</style>
