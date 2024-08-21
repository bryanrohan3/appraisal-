<template>
  <div class="layout wholesaler-layout">
    <WholesalerNavBar />
    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import WholesalerNavBar from "@/components/WholesalerNavBar.vue";

export default {
  name: "WholesalerLayout",
  components: {
    WholesalerNavBar,
  },
};
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh; /* Ensure layout takes up the full viewport height */
}

.main-content {
  flex: 1;
  margin-left: 250px; /* Match the width of the sidebar */
  padding: 2rem;
  box-sizing: border-box; /* Ensure padding is included in the width */
}
</style>
