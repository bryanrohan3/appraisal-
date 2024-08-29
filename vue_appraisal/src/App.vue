<template>
  <router-view />
</template>

<style lang="scss">
@import url("https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Special+Elite&display=swap");

html,
body {
  height: 100%;
  margin: 0;
  font-family: "Inter", sans-serif;
  background-color: #f5f5f5; /* Default background color */
}

#app {
  min-height: 100%;
}

.dealer-layout {
  background-color: #f5f5f5; /* Dealer background color */
}

.wholesaler-layout {
  background-color: #121212; /* Wholesaler background color */
  color: white; /* Ensure text is readable */
  min-height: 100vh; /* Ensure it takes the full viewport height */
  overflow: scroll;
  overflow-x: hidden;
  scrollbar-color: gray #121212;
}
</style>
