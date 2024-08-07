<template>
  <div class="layout">
    <DealerNavBar />
    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import DealerNavBar from "@/components/DealerNavBar.vue";

export default {
  name: "DealerLayout",
  components: {
    DealerNavBar,
  },
};
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh; /* Full viewport height */
}

main {
  flex: 1;
  margin-left: 250px; /* Match the width of the sidebar */
  padding: 2rem;
  box-sizing: border-box; /* Ensures padding is included in the width */
}
</style>
