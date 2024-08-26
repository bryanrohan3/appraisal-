<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Wholesalers List & Requests</h1>
      <div class="dealership-dropdown">
        <select
          class="input-dealership"
          v-model="selectedDealership"
          @change="fetchRequests"
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
    <div class="tabs">
      <!-- Tab Buttons -->
      <button
        class="tab-button"
        :class="{ active: activeTab === 'AddFriend' }"
        @click="setActiveTab('AddFriend')"
        v-if="this.userRole === 'wholesaler'"
      >
        Add Friend
      </button>
      <button
        class="tab-button"
        :class="{ active: activeTab === 'Friends' }"
        @click="setActiveTab('Friends')"
      >
        Friends
      </button>
      <button
        class="tab-button"
        :class="{ active: activeTab === 'Requests' }"
        @click="setActiveTab('Requests')"
      >
        Requests
      </button>
      <button
        class="tab-button"
        :class="{ active: activeTab === 'RejectedRequests' }"
        @click="setActiveTab('RejectedRequests')"
      >
        Rejected Requests
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <div v-if="activeTab === 'AddFriend'" class="tab-pane content-container">
        <div class="search-container">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search friends..."
            @input="debouncedSearch"
            class="search-input"
          />
        </div>
        <div v-if="searchResults.length" class="search-results">
          <ul>
            <li
              v-for="result in searchResults"
              :key="result.id"
              :class="[
                'result-item',
                result.type === 'wholesaler' ? 'wholesaler' : 'dealership',
              ]"
            >
              {{
                result.type === "dealership"
                  ? "Dealership: " + result.name
                  : result.type === "wholesaler"
                  ? "Wholesaler: " + result.name
                  : "Unknown Type: " + result.name
              }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Friends Tab -->
      <div v-if="activeTab === 'Friends'" class="tab-pane content-container">
        <table v-if="friends.length" class="data-table">
          <thead>
            <tr>
              <th>Sender</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in friends" :key="request.id">
              <td v-if="userRole === 'dealer'">{{ request.sender }}</td>
              <td class="wholesaler-friends" v-if="userRole === 'wholesaler'">
                {{
                  request.dealership
                    ? request.dealership_name
                    : request.recipient_wholesaler_username
                }}
              </td>

              <td>
                <button
                  class="action-button remove"
                  @click="respondToRequest(request.id, 'rejected')"
                >
                  Remove
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data-message">There are no friends.</p>
      </div>

      <!-- Requests Tab -->
      <div v-if="activeTab === 'Requests'" class="tab-pane content-container">
        <table v-if="pendingRequests.length" class="data-table">
          <thead>
            <tr>
              <th>Sender</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in pendingRequests" :key="request.id">
              <td>{{ request.sender }}</td>
              <td>
                <button
                  class="action-button accept"
                  @click="respondToRequest(request.id, 'accepted')"
                >
                  Accept
                </button>
                <button
                  class="action-button reject"
                  @click="respondToRequest(request.id, 'rejected')"
                >
                  Reject
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data-message">There are no pending requests.</p>
      </div>

      <!-- Rejected Requests Tab -->
      <div
        v-if="activeTab === 'RejectedRequests'"
        class="tab-pane content-container"
      >
        <table v-if="rejectedRequests.length" class="data-table">
          <thead>
            <tr>
              <th>Sender</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in rejectedRequests" :key="request.id">
              <td>{{ request.sender }}</td>
              <td>
                <button
                  class="action-button accept"
                  @click="respondToRequest(request.id, 'accepted')"
                >
                  Accept
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data-message">There are no rejected requests.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";
import { mapGetters } from "vuex";
import debounce from "lodash.debounce"; // Import lodash debounce

export default {
  name: "RequestsPage",
  data() {
    return {
      activeTab: "Friends", // Default active tab
      selectedDealership: "",
      dealershipOptions: [],
      friends: [],
      pendingRequests: [],
      rejectedRequests: [],
      searchQuery: "", // For search input
      searchResults: [], // Store search results
      wholesalerProfileInfo: null,
    };
  },
  computed: {
    ...mapGetters(["getUserProfile"]),
    userRole() {
      const userProfile = this.getUserProfile;
      return userProfile ? userProfile.role : "guest";
    },
  },
  methods: {
    setActiveTab(tab) {
      this.activeTab = tab;
      this.fetchRequests();
    },
    async fetchDealerProfileInfo() {
      if (this.userRole !== "dealer") {
        // Skip fetching dealer profile info if the user is not a dealer
        return;
      }

      try {
        const response = await axiosInstance.get(endpoints.dealerProfile);
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
        this.fetchRequests();
      } catch (error) {
        console.error("Error fetching dealer profile information:", error);
      }
    },
    async fetchWholesalerProfileInfo() {
      if (this.userRole !== "wholesaler") {
        // Skip fetching wholesaler profile info if the user is not a wholesaler
        return;
      }
      try {
        const response = await axiosInstance.get(endpoints.wholesalerProfile);
        this.wholesalerProfileInfo = response.data; // Store the wholesaler profile data
        console.log("Wholesaler Profile Response:", response.data);
      } catch (error) {
        console.error("Error fetching wholesaler profile information:", error);
      }
    },
    async fetchRequests() {
      try {
        let response;

        if (this.userRole === "dealer") {
          if (!this.selectedDealership) return; // Ensure dealership is selected
          response = await axiosInstance.get(
            endpoints.getReceivedRequests(this.selectedDealership)
          );
        } else if (this.userRole === "wholesaler") {
          if (this.activeTab === "Friends") {
            response = await axiosInstance.get(endpoints.getSentRequests); // Use the endpoint for wholesaler's sent requests in Friends tab
          } else if (this.activeTab === "Requests") {
            response = await axiosInstance.get(
              endpoints.wholesalerRequestsReceived
            ); // Use the endpoint for wholesaler's received requests in Requests tab
          } else {
            return; // If neither tab, do nothing
          }
        } else {
          return; // If neither dealer nor wholesaler, do nothing
        }

        const results = response.data.results || [];
        this.friends = results.filter(
          (request) => request.status === "accepted"
        );
        this.pendingRequests = results.filter(
          (request) => request.status === "pending"
        );
        this.rejectedRequests = results.filter(
          (request) => request.status === "rejected"
        );
      } catch (error) {
        console.error("Error fetching requests:", error);
      }
    },
    async respondToRequest(requestId, status) {
      try {
        await axiosInstance.put(endpoints.respondToRequest(requestId), {
          status,
        });
        this.fetchRequests(); // Refresh the requests list after responding
      } catch (error) {
        console.error("Error responding to request:", error);
      }
    },
    async searchWholesalers() {
      if (this.searchQuery.length === 0) {
        this.searchResults = [];
        return;
      }
      try {
        const response = await axiosInstance.get(
          endpoints.searchWholesalersAndDealerships(this.searchQuery) // Adjust your endpoint accordingly
        );
        this.searchResults = response.data.results || [];
      } catch (error) {
        console.error("Error searching wholesalers and dealerships:", error);
      }
    },

    debouncedSearch: debounce(function () {
      this.searchWholesalers();
    }, 300), // Debounce search by 300ms
  },
  mounted() {
    this.fetchDealerProfileInfo();
    this.fetchWholesalerProfileInfo();
  },
};
</script>

<style scoped>
.dashboard-container {
  margin: 0 auto;
  max-width: 1200px;
  padding: 20px;
  box-sizing: border-box;
}

.title {
  font-size: 24px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 600;
  margin-bottom: 20px;
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.input-dealership {
  padding: 10px 15px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #fff;
  color: #333;
}

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
  color: #eb5a58;
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

.data-table {
  width: 100%;
  border-collapse: collapse;
  border-radius: 4px;
  overflow: hidden;
}

.data-table thead {
  background-color: #f4f4f4;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  font-size: 12px;
}

.data-table th {
  font-weight: bold;
}

.data-table tbody tr:hover {
  background-color: #f1f1f1;
}

.action-button {
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  color: #fff;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.action-button.accept {
  background-color: #7cbf6b;
  margin-right: 20px; /* Adjust this value to set the space */
}

.action-button.reject {
  background-color: #f28b82;
}

.action-button.remove {
  background-color: #9e9e9e;
}

.action-button:hover {
  transform: scale(1.05);
}

.no-data-message {
  text-align: center;
  color: #666;
  font-style: italic;
}

.tab-pane {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.search-input {
  width: 98%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}

.search-results {
  background-color: #ffffff;
  border: 1px solid #ddd;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  color: #333;
}

ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
  color: #333;
}

.result-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
  color: #666;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item:hover {
  background-color: #f1f1f1;
}

/* Specific styles for wholesalers and dealerships */
.wholesaler {
  background-color: #e0f7fa; /* Light blue background for wholesalers */
}

.dealership {
  background-color: #c8e6c9; /* Light green background for dealerships */
}

.wholesaler-friends {
  color: #333;
}
</style>
