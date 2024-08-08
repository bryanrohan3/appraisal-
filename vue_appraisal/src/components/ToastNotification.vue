<template>
  <div v-if="visible" class="toast-notification">
    <p>{{ message }}</p>
  </div>
</template>

<script>
export default {
  props: ["message", "visible"],
  watch: {
    visible(newVal) {
      if (newVal) {
        setTimeout(() => {
          this.$emit("update:visible", false);
        }, 3000); // Hide the toast after 3 seconds
      }
    },
  },
};
</script>

<style scoped>
.toast-notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #28a745;
  color: #ffffff;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}
</style>
