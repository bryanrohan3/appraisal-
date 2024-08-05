import { createRouter, createWebHistory } from "vue-router";
import store from "@/store";
import LoginPage from "../views/LoginPage/LoginPage.vue";
import DealerDashboardPage from "../views/Dealer/DealerDashboardPage/DealerDashboardPage.vue";
import WholesalerDashboardPage from "../views/Wholesaler/WholesalerDashboardPage/WholesalerDashboardPage.vue";
import DealerLayout from "../components/Layouts/DealerLayout.vue";
import WholesalerLayout from "../components/Layouts/WholesalerLayout.vue";

const routes = [
  {
    path: "/login",
    name: "login",
    component: LoginPage,
  },
  {
    path: "/wholesaler",
    component: WholesalerLayout,
    meta: { requiresAuth: true, role: "wholesaler" },
    children: [
      {
        path: "dashboard",
        name: "WholesalerDashboardPage",
        component: WholesalerDashboardPage,
      },
    ],
  },
  {
    path: "/dealer",
    component: DealerLayout,
    meta: { requiresAuth: true, role: "dealer" },
    children: [
      {
        path: "dashboard",
        name: "DealerDashboardPage",
        component: DealerDashboardPage,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const userRole = store.getters.getUserRole;

  if (requiresAuth && !store.getters.getAuthToken) {
    next("/login");
  } else if (requiresAuth && userRole !== to.meta.role) {
    next("/login"); // Redirect to login if role does not match
  } else {
    next();
  }
});

export default router;
