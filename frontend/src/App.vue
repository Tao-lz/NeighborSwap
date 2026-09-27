<template>
  <div class="app">
    <header class="header">
      <div class="brand" @click="$router.push('/')">
        <span class="logo">🏘</span>
        <span>邻里交换</span>
      </div>
      <nav class="nav">
        <router-link to="/">首页</router-link>
        <router-link to="/publish">发布</router-link>
        <router-link to="/mine">我的</router-link>
        <router-link to="/dashboard">看板</router-link>
      </nav>
      <div class="user">
        <template v-if="userStore.isLoggedIn">
          <span class="nickname">{{ userStore.nickname }}</span>
          <el-button link size="small" @click="userStore.logout()">退出</el-button>
        </template>
        <el-button v-else size="small" @click="showLogin = true">登录</el-button>
      </div>
    </header>
    <main class="main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="footer">邻里交换 · 让闲置物品流动起来</footer>
    <LoginDialog v-model="showLogin" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from './stores/user'
import LoginDialog from './components/LoginDialog.vue'

const userStore = useUserStore()
const showLogin = ref(false)

onMounted(() => {
  if (!userStore.isLoggedIn) showLogin.value = true
})
</script>

<style>
:root {
  --brand: #10b981;
  --brand-strong: #059669;
  --ink: #1f2937;
}
* {
  box-sizing: border-box;
}
body {
  margin: 0;
  color: #333;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-color: #f5f7f6;
  background-image:
    radial-gradient(1200px 400px at 50% -100px, #e7f6ef 0, rgba(231, 246, 239, 0) 70%),
    linear-gradient(180deg, #f0f7f4 0, #f5f7f6 300px);
  background-attachment: fixed;
}
.header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 24px;
  height: 60px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  box-shadow: 0 1px 0 rgba(16, 185, 129, 0.08), 0 2px 16px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 10;
}
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 18px;
  color: var(--ink);
  cursor: pointer;
}
.logo {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: linear-gradient(135deg, #10b981, #34d399);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
}
.nav {
  display: flex;
  gap: 4px;
}
.nav a {
  color: #6b7280;
  text-decoration: none;
  padding: 7px 14px;
  border-radius: 999px;
  font-size: 14px;
  transition: all 0.15s;
}
.nav a:hover {
  background: #f3f4f6;
  color: #111827;
}
.nav a.router-link-active {
  color: var(--brand-strong);
  background: #ecfdf5;
  font-weight: 600;
}
.user {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}
.nickname {
  color: #333;
}
.main {
  max-width: 1100px;
  margin: 24px auto 8px;
  padding: 0 24px;
  min-height: calc(100vh - 220px);
}
.footer {
  text-align: center;
  color: #9ca3af;
  font-size: 12px;
  padding: 20px 0 28px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
@media (max-width: 640px) {
  .header {
    flex-wrap: wrap;
    height: auto;
    padding: 10px 16px;
    gap: 8px 12px;
  }
  .nav {
    order: 3;
    width: 100%;
    justify-content: space-between;
  }
  .nav a {
    padding: 6px 12px;
  }
  .main {
    padding: 0 12px;
    margin-top: 16px;
  }
}
</style>
