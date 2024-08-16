<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Management Dealer Panel</h1>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <!-- Tab Buttons -->
      <button
        class="tab-button"
        :class="{ active: activeTab === 'CreateUser' }"
        @click="setActiveTab('CreateUser')"
      >
        Create User
      </button>
      <button
        class="tab-button"
        :class="{ active: activeTab === 'ManageDealership' }"
        @click="setActiveTab('ManageDealership')"
      >
        Manage Dealership
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Create User Tab -->
      <div v-if="activeTab === 'CreateUser'" class="tab-pane content-container">
        <!-- Content for Create User -->
        <form @submit.prevent="createUser">
          <div>
            <label for="username">Username:</label>
            <input
              v-model="newUser.username"
              type="text"
              id="username"
              required
            />
          </div>
          <div>
            <label for="password">Password:</label>
            <input
              v-model="newUser.password"
              type="password"
              id="password"
              required
            />
          </div>
          <div>
            <label for="email">Email:</label>
            <input v-model="newUser.email" type="email" id="email" required />
          </div>
          <div>
            <label for="first_name">First Name:</label>
            <input
              v-model="newUser.first_name"
              type="text"
              id="first_name"
              required
            />
          </div>
          <div>
            <label for="last_name">Last Name:</label>
            <input
              v-model="newUser.last_name"
              type="text"
              id="last_name"
              required
            />
          </div>
          <div>
            <label for="phone">Phone:</label>
            <input v-model="newUser.phone" type="text" id="phone" required />
          </div>
          <div>
            <label for="role">Role:</label>
            <select v-model="newUser.role" id="role" required>
              <option value="M">Management</option>
              <option value="S">Sales</option>
            </select>
          </div>

          <div class="dealership-dropdown">
            <label for="dealership">Select Dealership:</label>
            <select
              id="dealership"
              v-model="newUser.dealership"
              class="input-dealership"
              required
            >
              <option disabled value="">Select Dealership</option>
              <option
                v-for="option in dealershipOptions"
                :key="option.id"
                :value="option.id"
              >
                {{ option.name }}
              </option>
            </select>
          </div>

          <button type="submit">Create User</button>
        </form>
      </div>

      <!-- Manage Dealership Tab -->
      <div
        v-if="activeTab === 'ManageDealership'"
        class="tab-pane content-container"
      >
        <p>This is where you can manage dealership settings.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";

export default {
  name: "ManagementPage",
  data() {
    return {
      activeTab: "CreateUser",
      newUser: {
        username: "",
        password: "",
        email: "",
        first_name: "",
        last_name: "",
        phone: "",
        role: "",
        dealership: "",
      },
      dealershipOptions: [],
      formData: {},
    };
  },
  methods: {
    setActiveTab(tab) {
      this.activeTab = tab;
    },
    async fetchDealerProfileInfo() {
      try {
        const response = await axiosInstance.get(endpoints.dealerProfile);
        this.formData = response.data;

        const dealershipIds = response.data.dealerships || [];
        const dealershipNames = response.data.dealership_names || [];

        const dealershipMap = new Map(
          dealershipNames.map(({ id, dealership_name }) => [
            id,
            dealership_name,
          ])
        );

        this.dealershipOptions = dealershipIds.map((id) => ({
          id: id,
          name: dealershipMap.get(id) || `Dealership ${id}`,
        }));

        this.newUser.dealership =
          this.dealershipOptions.length > 0 ? this.dealershipOptions[0].id : "";
      } catch (error) {
        console.error("Error fetching dealer profile information:", error);
      }
    },
    async createUser() {
      try {
        const payload = {
          user: {
            username: this.newUser.username,
            password: this.newUser.password,
            email: this.newUser.email,
            first_name: this.newUser.first_name,
            last_name: this.newUser.last_name,
          },
          phone: this.newUser.phone,
          role: this.newUser.role,
          dealerships: [this.newUser.dealership], // Updated to dealerships array
        };

        // Log the payload to the console
        console.log("Creating user with payload:", payload);

        const response = await axiosInstance.post(
          endpoints.dealerCreateProfile,
          payload
        );
        alert("User created successfully!");

        // Optionally, log the response to see the returned data
        console.log("User creation response:", response.data);
      } catch (error) {
        console.error("Error creating user:", error);
        alert("Failed to create user. Please try again.");
      }
    },
  },
  mounted() {
    this.fetchDealerProfileInfo();
  },
};
</script>

<style scoped>
.dashboard-container {
  margin-left: auto;
  margin-right: auto;
  max-width: 1200px;
  padding: 20px;
  box-sizing: border-box;
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title {
  font-size: 24px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 600;
}

/* Tab styles */
.tabs {
  display: flex;
  margin-bottom: 20px;
  justify-content: flex-start;
}

.tab-button {
  background-color: transparent;
  border: none;
  padding: 12px 24px;
  margin-right: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #b0b0b0;
  position: relative;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.tab-button:hover {
  background-color: #f0f0f0;
}

.tab-button.active {
  color: #333;
  font-weight: 600;
}

.tab-button::after {
  content: "";
  display: block;
  height: 2px;
  background-color: #eb5a58;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  transform: scaleX(0);
  transform-origin: bottom left;
  transition: transform 0.3s ease;
}

.tab-button.active::after {
  transform: scaleX(1);
}

.tab-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.content-container {
  background-color: #fff;
  border-radius: 4px;
}
</style>
