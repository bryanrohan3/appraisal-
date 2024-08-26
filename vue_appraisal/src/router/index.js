import { createRouter, createWebHistory } from "vue-router";
import store from "@/store";
import LoginPage from "../views/LoginPage/LoginPage.vue";
import DealerDashboardPage from "../views/Dealer/DealerDashboardPage/DealerDashboardPage.vue";
import WholesalerDashboardPage from "../views/Wholesaler/WholesalerDashboardPage/WholesalerDashboardPage.vue";
import DealerLayout from "../components/Layouts/DealerLayout.vue";
import WholesalerLayout from "../components/Layouts/WholesalerLayout.vue";
import CreateAppraisalPage from "@/views/Dealer/CreateAppraisalPage/CreateAppraisalPage.vue";
import AppraisalsPage from "@/views/Dealer/AppraisalsPage/AppraisalsPage.vue";
import AppraisalViewPage from "@/views/Dealer/AppraisalViewPage/AppraisalViewPage.vue";
import AnalyticsPage from "@/views/Dealer/AnalyticsPage/AnalyticsPage.vue";
import RequestsPage from "@/views/Dealer/RequestsPage/RequestsPage.vue";
import ManagementPage from "@/views/Dealer/ManagementPage/ManagementPage.vue";
import ProfilePage from "@/views/Dealer/ProfilePage/ProfilePage.vue";

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
      {
        path: "appraisals",
        name: "WholesalerAppraisalsPage",
        component: AppraisalsPage,
      },
      {
        path: "requests",
        name: "WholesalerRequestsPage",
        component: RequestsPage,
      },
    ],
  },
  {
    path: "",
    component: DealerLayout,
    meta: { requiresAuth: true, role: "dealer" },
    children: [
      {
        path: "dashboard",
        name: "DealerDashboardPage",
        component: DealerDashboardPage,
      },
      {
        path: "create-appraisal",
        name: "CreateAppraisalPage",
        component: AppraisalViewPage,
      },
      {
        path: "appraisals",
        name: "AppraisalsPage",
        component: AppraisalsPage,
      },
      {
        path: "appraisals/:id",
        name: "AppraisalViewPage",
        component: AppraisalViewPage,
      },
      {
        path: "analytics",
        name: "AnalyticsPage",
        component: AnalyticsPage,
      },
      {
        path: "requests",
        name: "RequestsPage",
        component: RequestsPage,
      },
      {
        path: "profile",
        name: "ProfilePage",
        component: ProfilePage,
      },
      {
        path: "management",
        name: "ManagementPage",
        component: ManagementPage,
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
