<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Management Dealer Panel</h1>
      <div class="dealership-dropdown">
        <select
          class="input-dealership"
          v-model="selectedDealership"
          @change="fetchDealers"
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
        <form @submit.prevent="createUser" class="customer-details-form">
          <!-- Row 1: First Name, Last Name -->
          <div class="form-row-horizontal">
            <div class="form-group">
              <label for="first_name">First Name:</label>
              <input
                v-model="newUser.first_name"
                type="text"
                id="first_name"
                required
              />
            </div>
            <div class="form-group">
              <label for="last_name">Last Name:</label>
              <input
                v-model="newUser.last_name"
                type="text"
                id="last_name"
                required
              />
            </div>
          </div>

          <!-- Row 2: Username, Password -->
          <div class="form-row-horizontal">
            <div class="form-group">
              <label for="username">Username:</label>
              <input
                v-model="newUser.username"
                type="text"
                id="username"
                required
              />
            </div>
            <div class="form-group">
              <label for="password">Password:</label>
              <input
                v-model="newUser.password"
                type="password"
                id="password"
                required
              />
            </div>
          </div>

          <!-- Row 3: Phone, Email -->
          <div class="form-row-horizontal">
            <div class="form-group">
              <label for="phone">Phone:</label>
              <input v-model="newUser.phone" type="text" id="phone" required />
            </div>
            <div class="form-group">
              <label for="email">Email:</label>
              <input v-model="newUser.email" type="email" id="email" required />
            </div>
          </div>

          <!-- Row 4: Role, Dealership -->
          <div class="form-row-horizontal">
            <div class="form-group">
              <label for="role">Role:</label>
              <select v-model="newUser.role" id="role" required>
                <option value="M">Management</option>
                <option value="S">Sales</option>
              </select>
            </div>
            <div class="form-group dealership-dropdown">
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
          </div>

          <button type="submit">Create User</button>
        </form>
      </div>

      <!-- Manage Dealership Tab -->
      <div
        v-if="activeTab === 'ManageDealership'"
        class="tab-pane content-container"
      >
        <!-- Filter Button and Role Dropdown -->
        <div class="filter-container">
          <select
            v-model="selectedRole"
            @change="applyFilter"
            class="role-filter"
          >
            <option value="">All Roles</option>
            <option value="S">Sales</option>
            <option value="M">Management</option>
          </select>
        </div>

        <!-- Dealers Table -->
        <table class="table table-dealer">
          <thead>
            <tr class="table-header">
              <th>Username</th>
              <th>First Name</th>
              <th>Last Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="dealer in filteredDealers" :key="dealer.user.id">
              <td>{{ dealer.user.username }}</td>
              <td>{{ dealer.user.first_name }}</td>
              <td>{{ dealer.user.last_name }}</td>
              <td>{{ dealer.user.email }}</td>
              <td>{{ dealer.phone }}</td>
              <td>{{ dealer.role === "S" ? "Sales" : "Management" }}</td>
              <td>
                <!-- Actions Dropdown Button -->
                <button @click="toggleDropdown(dealer.user.id)">
                  <img
                    src="@/assets/dots.svg"
                    alt="Actions"
                    class="actions-icon"
                  />
                </button>
                <!-- Actions Dropdown Menu -->
                <div
                  v-if="dropdownOpen === dealer.user.id"
                  class="dropdown-menu"
                >
                  <button @click="promoteDealer(dealer.user.id)">
                    Promote
                  </button>
                  <button @click="demoteDealer(dealer.user.id)">Demote</button>
                  <button @click="deleteDealer(dealer.user.id)">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <span class="total-records"
          >Total Dealers: {{ filteredDealers.length }}</span
        >
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
      dealers: [],
      selectedDealership: "",
      selectedRole: "", // Added to store the selected role for filtering
      filteredDealers: [], // Added to store filtered dealers
      totalDealers: 0,
      dropdownOpen: null,
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

        this.selectedDealership =
          this.dealershipOptions.length > 0 ? this.dealershipOptions[0].id : "";
        this.fetchDealers();

        this.newUser.dealership =
          this.dealershipOptions.length > 0 ? this.dealershipOptions[0].id : "";
      } catch (error) {
        console.error("Error fetching dealer profile information:", error);
      }
    },

    async fetchDealers() {
      if (!this.selectedDealership) return;

      try {
        const response = await axiosInstance.get(
          endpoints.dealersByDealership(this.selectedDealership)
        );

        this.dealers = response.data;
        this.applyFilter(); // Apply filter when dealers are fetched
      } catch (error) {
        console.error("Error fetching dealers:", error);
      }
    },

    applyFilter() {
      if (this.selectedRole) {
        this.filteredDealers = this.dealers.filter(
          (dealer) => dealer.role === this.selectedRole
        );
      } else {
        this.filteredDealers = this.dealers;
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
    // Action Dropdown
    toggleDropdown(userId) {
      this.dropdownOpen = this.dropdownOpen === userId ? null : userId;
    },
    async promoteDealer(userId) {
      try {
        // Call the promote endpoint
        const response = await axiosInstance.post(
          endpoints.promoteDealer(userId)
        );
        alert("Dealer promoted successfully!");
        // Optionally, refresh the list of dealers
        this.fetchDealers();
        console.log(`Promoted dealer with ID ${userId}`);
      } catch (error) {
        console.error("Error promoting dealer:", error);
        alert("Failed to promote dealer. Please try again.");
      }
    },
    async demoteDealer(userId) {
      try {
        // Call the demote endpoint
        const response = await axiosInstance.post(
          endpoints.demoteDealer(userId)
        );
        alert("Dealer demoted successfully!");
        this.fetchDealers();
        console.log(`Demoted dealer with ID ${userId}`);
      } catch (error) {
        console.error("Error demoting dealer:", error);

        if (error.response) {
          if (
            error.response.data.error ===
            "Dealer is already a Sales Dealer and cannot be demoted further"
          ) {
            alert(
              "This dealer is already a Sales Dealer and cannot be demoted further."
            );
          } else if (
            error.response.data.error === "Dealer is not a Management Dealer"
          ) {
            alert("This dealer is not a Management Dealer.");
          } else if (error.response.status === 404) {
            alert("Dealer not found or not eligible for demotion.");
          } else {
            alert("Failed to demote dealer. Please try again.");
          }
        } else {
          alert("Failed to demote dealer. Please try again.");
        }
      }
    },
    async deleteDealer(userId) {
      try {
        // Call the delete endpoint
        const response = await axiosInstance.patch(
          endpoints.deactivateDealer(userId)
        );
        alert("Dealer deleted successfully!");
        // Optionally, refresh the list of dealers
        this.fetchDealers();
        console.log(`Deleted dealer with ID ${userId}`);
      } catch (error) {
        console.error("Error deleting dealer:", error);
        alert("Failed to delete dealer. Please try again.");
      }
    },
  },
  created() {
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

/* Input styles */
input[type="text"],
input[type="password"],
input[type="email"],
select {
  width: 100%;
  padding: 10px;
  margin-top: 8px;
  margin-bottom: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
}

input[type="text"]:focus,
input[type="password"]:focus,
input[type="email"]:focus,
select:focus {
  border-color: #eb5a58;
  outline: none;
}

button[type="submit"] {
  padding: 10px 20px;
  background-color: #eb5a58;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

button[type="submit"]:hover {
  background-color: #d14c4a;
}

label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #7d7b7b;
  font-weight: 600;
}
/* Filter Controls */
.filter-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
  width: 20%;
}

.role-filter {
  margin-right: 1rem;
  padding: 0.5rem;
  font-size: 12px;
}

.total-records {
  margin-top: 20px;
  text-align: center;
  font-size: 12px;
  color: #999;
}

/* actions dropdown */
.actions-icon {
  width: 20px;
  height: 20px;
}

.dropdown-menu {
  display: flex;
  flex-direction: column;
  position: absolute;
  background: white;
  border: 1px solid #ddd;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 5px;
  z-index: 1000;
}

.dropdown-menu button {
  background: none;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
}

.dropdown-menu button:hover {
  background-color: #f0f0f0;
}

.form-row-horizontal {
  display: flex;
  gap: 20px;
}

.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
