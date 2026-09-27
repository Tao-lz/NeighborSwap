<template>
  <div v-loading="loading" class="detail">
    <template v-if="item">
      <el-card class="main-card">
        <div class="layout">
          <div class="img-box">
            <el-image v-if="item.image_url" :src="item.image_url" fit="cover" class="img" />
            <div v-else class="img img-placeholder">无图</div>
          </div>
          <div class="info">
            <div class="name-row">
              <h2 class="name">{{ item.name }}</h2>
              <FreshnessTag :created-at="item.created_at" />
              <el-tag v-if="item.status === 'given'" type="info">已送出</el-tag>
            </div>
            <div class="price">{{ priceText }}</div>
            <p class="desc">{{ item.description }}</p>
            <div class="meta">
              <span>发布者：{{ item.owner_nickname }}</span>
              <span>{{ item.want_count }} 人想要</span>
            </div>

            <div v-if="!isOwner" class="actions">
              <el-button
                v-if="item.status === 'available' && !item.wanted_by_me"
                type="primary"
                @click="want"
              >
                我想要
              </el-button>
              <el-button v-else-if="item.wanted_by_me" disabled>已表达想要</el-button>
              <el-tag v-if="item.status === 'given'" type="info">该物品已送出</el-tag>
            </div>

            <div v-if="isOwner && item.status === 'available'" class="actions">
              <el-button type="warning" @click="markGiven">标记已送出</el-button>
              <el-button @click="openWants">查看谁想要 ({{ item.want_count }})</el-button>
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="faq-card">
        <template #header>智能问答 · FAQ</template>
        <div class="faq-questions">
          <el-button size="small" @click="askFaq('还在吗？')">还在吗？</el-button>
          <el-button size="small" @click="askFaq('能自提吗？')">能自提吗？</el-button>
          <el-button size="small" @click="askFaq('能刀吗？')">能刀吗？</el-button>
        </div>
        <div class="faq-input">
          <el-input
            v-model="faqQuestion"
            placeholder="其它问题…"
            maxlength="200"
            @keyup.enter="askFaq()"
          />
          <el-button type="primary" :loading="asking" @click="askFaq()">提问</el-button>
        </div>
        <div v-if="faqAnswer" class="faq-answer">{{ faqAnswer }}</div>
      </el-card>

      <el-card class="comments-card">
        <template #header>留言板</template>
        <div class="comment-input">
          <el-input
            v-model="commentText"
            placeholder="围绕物品提问或留言"
            maxlength="1000"
            @keyup.enter="postComment"
          />
          <el-button type="primary" @click="postComment">发送</el-button>
        </div>
        <div class="comment-list">
          <div v-for="c in comments" :key="c.id" class="comment">
            <span class="c-user">{{ c.user_nickname }}</span>
            <span class="c-content">{{ c.content }}</span>
            <span class="c-time">{{ formatTime(c.created_at) }}</span>
          </div>
          <el-empty v-if="comments.length === 0" description="还没有留言" :image-size="60" />
        </div>
      </el-card>
    </template>

    <el-empty v-else-if="!loading" description="物品不存在或已删除" />

    <el-dialog v-model="showWants" title="谁想要" width="420px">
      <div v-for="w in wants" :key="w.id" class="want-row">
        <span>{{ w.user_nickname }}</span>
        <el-button v-if="w.status === 'wanted'" type="success" size="small" @click="confirm(w)">
          确认成交
        </el-button>
        <el-tag v-else type="success" size="small">已成交</el-tag>
      </div>
      <el-empty v-if="wants.length === 0" description="还没有人想要" :image-size="60" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'
import { useUserStore } from '../stores/user'
import FreshnessTag from '../components/FreshnessTag.vue'

const route = useRoute()
const userStore = useUserStore()

const item = ref(null)
const comments = ref([])
const wants = ref([])
const loading = ref(false)
const commentText = ref('')
const showWants = ref(false)
const faqQuestion = ref('')
const faqAnswer = ref('')
const asking = ref(false)

const itemId = computed(() => route.params.id)
const isOwner = computed(() => item.value && userStore.userId === item.value.owner_id)

const priceText = computed(() => {
  if (!item.value) return ''
  if (item.value.trade_type === 'free') return '免费送'
  if (item.value.trade_type === 'offer') return '随便给'
  return `¥${item.value.price}`
})

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/items/${itemId.value}`)
    item.value = data
  } catch (e) {
    item.value = null
  } finally {
    loading.value = false
  }
}

async function loadComments() {
  const { data } = await api.get(`/items/${itemId.value}/comments`)
  comments.value = data
}

async function want() {
  if (!userStore.isLoggedIn) return ElMessage.warning('请先登录')
  try {
    await api.post(`/items/${itemId.value}/wants`)
    ElMessage.success('已表达想要，等待发布者确认')
    await load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

async function markGiven() {
  try {
    await ElMessageBox.confirm('确认将该物品标记为已送出吗？', '提示', { type: 'warning' })
  } catch (e) {
    return
  }
  await api.patch(`/items/${itemId.value}`, { status: 'given' })
  ElMessage.success('已标记送出')
  await load()
}

async function openWants() {
  showWants.value = true
  const { data } = await api.get(`/items/${itemId.value}/wants`)
  wants.value = data
}

async function confirm(w) {
  try {
    await ElMessageBox.confirm(`确认与「${w.user_nickname}」成交？`, '确认成交', { type: 'success' })
  } catch (e) {
    return
  }
  await api.post(`/wants/${w.id}/confirm`)
  ElMessage.success('成交成功')
  showWants.value = false
  await load()
}

async function askFaq(question) {
  const q = (question || faqQuestion.value).trim()
  if (!q) return
  asking.value = true
  faqAnswer.value = ''
  try {
    const { data } = await api.post('/llm/faq', {
      item_id: Number(itemId.value),
      question: q,
    })
    faqAnswer.value = data.answer
  } catch (e) {
    faqAnswer.value = e.response?.data?.detail || '暂时无法回答'
  } finally {
    asking.value = false
  }
}

async function postComment() {
  if (!userStore.isLoggedIn) return ElMessage.warning('请先登录')
  const content = commentText.value.trim()
  if (!content) return
  try {
    await api.post(`/items/${itemId.value}/comments`, { content })
    commentText.value = ''
    await loadComments()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发送失败')
  }
}

function formatTime(iso) {
  const d = new Date(iso)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${d.getMonth() + 1}-${d.getDate()} ${hh}:${mm}`
}

onMounted(() => {
  load()
  loadComments()
})
</script>

<style scoped>
.layout {
  display: flex;
  gap: 24px;
}
@media (max-width: 640px) {
  .layout {
    flex-direction: column;
    gap: 16px;
  }
  .img-box {
    width: 100%;
  }
}
.img-box {
  width: 320px;
  height: 240px;
  flex-shrink: 0;
  background: #f5f5f5;
  border-radius: 6px;
  overflow: hidden;
}
.img {
  width: 100%;
  height: 100%;
}
.img-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
  height: 100%;
}
.info {
  flex: 1;
}
.name-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.name {
  margin: 0;
}
.price {
  color: #f56c6c;
  font-weight: 700;
  font-size: 24px;
  margin: 12px 0;
}
.desc {
  color: #555;
  line-height: 1.6;
  white-space: pre-wrap;
}
.meta {
  color: #999;
  font-size: 13px;
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}
.actions {
  margin-top: 8px;
}
.faq-card {
  margin-top: 16px;
}
.faq-questions {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.faq-input {
  display: flex;
  gap: 12px;
}
.faq-answer {
  margin-top: 12px;
  padding: 10px 12px;
  background: #f0f9ff;
  border-radius: 6px;
  color: #333;
  line-height: 1.6;
}
.comments-card {
  margin-top: 16px;
}
.comment-input {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.comment {
  display: flex;
  gap: 12px;
  align-items: baseline;
  padding-bottom: 8px;
  border-bottom: 1px dashed #eee;
}
.c-user {
  color: #409eff;
  font-weight: 600;
  flex-shrink: 0;
}
.c-content {
  color: #333;
  flex: 1;
  word-break: break-all;
}
.c-time {
  color: #bbb;
  font-size: 12px;
  flex-shrink: 0;
}
.want-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
</style>
