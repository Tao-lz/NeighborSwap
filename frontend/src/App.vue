<template>
  <div class="app">
    <header class="header">
      <div class="brand" @click="$router.push('/')">🏘 邻里交换</div>
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
      <router-view />
    </main>
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
* {
  box-sizing: border-box;
}
body {
  margin: 0;
  background: #f7f8fa;
  color: #333;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 0 24px;
  height: 56px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 10;
}
.brand {
  font-weight: 700;
  font-size: 18px;
  cursor: pointer;
}
.nav {
  display: flex;
  gap: 20px;
}
.nav a {
  color: #666;
  text-decoration: none;
}
.nav a.router-link-active {
  color: #409eff;
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
  margin: 24px auto;
  padding: 0 24px;
}
</style>
