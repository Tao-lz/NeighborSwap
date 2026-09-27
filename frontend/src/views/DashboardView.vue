<template>
  <div v-loading="loading" class="dash">
    <div class="stats">
      <el-card class="stat" shadow="hover">
        <div class="stat-inner">
          <div class="stat-icon c-blue"><el-icon :size="22"><Upload /></el-icon></div>
          <div class="stat-info">
            <div class="stat-num">{{ data.month_published }}</div>
            <div class="stat-label">本月发布</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat" shadow="hover">
        <div class="stat-inner">
          <div class="stat-icon c-green"><el-icon :size="22"><CircleCheck /></el-icon></div>
          <div class="stat-info">
            <div class="stat-num">{{ data.month_given }}</div>
            <div class="stat-label">本月成交</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat" shadow="hover">
        <div class="stat-inner">
          <div class="stat-icon c-orange"><el-icon :size="22"><Box /></el-icon></div>
          <div class="stat-info">
            <div class="stat-num">{{ data.current_available }}</div>
            <div class="stat-label">当前在售</div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="highlights">
      <el-card class="hl" shadow="hover">
        <template #header>
          <div class="hl-head"><el-icon><Timer /></el-icon>最快被领走的物品</div>
        </template>
        <div v-if="data.fastest_given">
          <div class="hl-name">{{ data.fastest_given.name }}</div>
          <div class="hl-sub">上架 {{ duration(data.fastest_given) }} 后被领走</div>
        </div>
        <el-empty v-else description="暂无成交记录" :image-size="60" />
      </el-card>

      <el-card class="hl" shadow="hover">
        <template #header>
          <div class="hl-head"><el-icon><StarFilled /></el-icon>最多人想要（尚未成交）</div>
        </template>
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
  border: none;
  border-radius: 12px;
}
.stat-inner {
  display: flex;
  align-items: center;
  gap: 14px;
}
.stat-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.c-blue {
  color: #2563eb;
  background: #eff6ff;
}
.c-green {
  color: #16a34a;
  background: #f0fdf4;
}
.c-orange {
  color: #f59e0b;
  background: #fffbeb;
}
.stat-num {
  font-size: 30px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}
.stat-label {
  color: #9ca3af;
  margin-top: 6px;
  font-size: 13px;
}
.highlights {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.hl {
  border: none;
  border-radius: 12px;
}
.hl-head {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #374151;
  font-weight: 600;
}
.hl-head .el-icon {
  color: var(--el-color-primary);
}
.hl-name {
  font-weight: 600;
  font-size: 18px;
}
.hl-sub {
  color: #999;
  margin-top: 8px;
}
@media (max-width: 640px) {
  .stats {
    grid-template-columns: 1fr;
  }
  .highlights {
    grid-template-columns: 1fr;
  }
}
</style>
