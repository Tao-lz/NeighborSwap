<template>
  <div class="publish">
    <el-card class="form-card">
      <template #header>发布闲置物品</template>
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="例如：九成新电风扇" maxlength="100" />
        </el-form-item>
        <el-form-item label="交易方式" required>
          <div class="type-row">
            <el-radio-group v-model="form.trade_type">
              <el-radio-button value="free">免费送</el-radio-button>
              <el-radio-button value="offer">随便给</el-radio-button>
              <el-radio-button value="priced">标价</el-radio-button>
            </el-radio-group>
            <el-button size="small" :loading="suggesting" @click="suggestPrice">
              ✨ 智能定价
            </el-button>
          </div>
          <div v-if="priceTip" class="price-tip">💡 {{ priceTip }}</div>
        </el-form-item>
        <el-form-item v-if="form.trade_type === 'priced'" label="价格">
          <el-input-number v-model="form.price" :min="0" :precision="0" />
          <span class="unit">元</span>
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="新旧程度、使用情况、自提地点等"
            maxlength="1000"
          />
          <el-button size="small" class="polish-btn" :loading="polishing" @click="polish">
            ✨ 优化描述
          </el-button>
        </el-form-item>
        <el-form-item label="图片">
          <div class="upload-row">
            <el-upload :show-file-list="false" :http-request="uploadImage" accept="image/*">
              <el-button :loading="uploading">上传图片</el-button>
            </el-upload>
            <div v-if="form.image_url" class="preview">
              <el-image :src="form.image_url" fit="cover" class="preview-img" />
              <el-button link type="danger" @click="form.image_url = null">移除</el-button>
            </div>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submit">发布</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const submitting = ref(false)
const uploading = ref(false)
const suggesting = ref(false)
const polishing = ref(false)
const priceTip = ref('')

const form = reactive({
  name: '',
  trade_type: 'free',
  price: 0,
  description: '',
  image_url: null,
})

async function uploadImage(options) {
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', options.file)
    const { data } = await api.post('/images', fd)
    form.image_url = data.url
    ElMessage.success('图片上传成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function suggestPrice() {
  if (!form.name.trim() || !form.description.trim()) {
    return ElMessage.warning('请先填写名称和描述')
  }
  suggesting.value = true
  try {
    const { data } = await api.post('/llm/price-suggest', {
      name: form.name.trim(),
      description: form.description.trim(),
    })
    form.trade_type = data.trade_type
    if (data.trade_type === 'priced' && data.price_min != null) {
      form.price = Math.round((data.price_min + data.price_max) / 2)
    }
    priceTip.value = data.reason || ''
    ElMessage.success('已给出定价建议')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '定价建议失败')
  } finally {
    suggesting.value = false
  }
}

async function polish() {
  if (!form.description.trim()) return ElMessage.warning('请先填写描述')
  polishing.value = true
  try {
    const { data } = await api.post('/llm/polish', {
      description: form.description.trim(),
    })
    form.description = data.polished
    ElMessage.success('描述已优化')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '优化失败')
  } finally {
    polishing.value = false
  }
}

async function submit() {
  if (!userStore.isLoggedIn) return ElMessage.warning('请先登录')
  if (!form.name.trim()) return ElMessage.warning('请填写名称')
  if (!form.description.trim()) return ElMessage.warning('请填写描述')
  submitting.value = true
  try {
    await api.post('/items', {
      name: form.name.trim(),
      description: form.description.trim(),
      trade_type: form.trade_type,
      price: form.trade_type === 'priced' ? form.price : null,
      image_url: form.image_url,
    })
    ElMessage.success('发布成功')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '发布失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-card {
  max-width: 640px;
  margin: 0 auto;
}
.unit {
  margin-left: 8px;
  color: #666;
}
.type-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.price-tip {
  margin-top: 8px;
  color: #e6a23c;
  font-size: 13px;
}
.polish-btn {
  margin-top: 8px;
}
.upload-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.preview {
  display: flex;
  align-items: center;
  gap: 8px;
}
.preview-img {
  width: 80px;
  height: 80px;
  border-radius: 4px;
}
</style>
