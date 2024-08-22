<template>
  <div class="invite-container">
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
      <table class="data-table">
        <thead>
          <tr>
            <th>Wholesaler</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="friend in searchResults" :key="friend.id">
            <td>{{ friend.sender }}</td>
            <td>
              <button @click="addFriend(friend)" class="add-button">
                Add {{ friend.sender }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="selected-friends">
      <p class="titles">Selected Wholesalers</p>
      <table class="data-table">
        <tbody>
          <tr v-for="friend in selectedFriends" :key="friend.id">
            <td>{{ friend.sender }}</td>
            <td>
              <button @click="removeFriend(friend.id)" class="remove-button">
                Remove
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <button @click="sendInvitations" class="send-button">
      Send Invitations
    </button>

    <div v-if="invitedWholesalers.length" class="invited-list">
      <p class="titles">Invited Wholesalers Awaiting Offers</p>
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Invited At</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="wholesaler in invitedWholesalers" :key="wholesaler.id">
            <td>{{ wholesaler.id }}</td>
            <td>{{ wholesaler.username }}</td>
            <td>{{ formatDate(wholesaler.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";
import debounce from "lodash.debounce";

export default {
  name: "InviteWholesaler",
  props: {
    dealershipId: {
      type: Number,
      required: true,
    },
    appraisalId: {
      type: Number,
      required: true,
    },
    appraisal: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      searchQuery: "",
      searchResults: [],
      selectedFriends: [],
      invitedWholesalers: [],
    };
  },
  watch: {
    appraisal: {
      handler(newVal) {
        if (newVal && newVal.invites) {
          this.invitedWholesalers = newVal.invites;
        }
      },
      immediate: true,
    },
  },
  methods: {
    async fetchFriends() {
      if (!this.searchQuery) return;
      try {
        const response = await axiosInstance.get(
          endpoints.getReceivedRequests(this.dealershipId),
          {
            params: {
              search: this.searchQuery,
            },
          }
        );
        this.searchResults = response.data.results.filter(
          (request) => request.status === "accepted"
        );
      } catch (error) {
        console.error("Error fetching friends:", error);
      }
    },
    debouncedSearch: debounce(function () {
      this.fetchFriends();
    }, 300),
    addFriend(friend) {
      if (!this.selectedFriends.some((f) => f.id === friend.id)) {
        this.selectedFriends.push(friend);
      }
    },
    removeFriend(friendId) {
      this.selectedFriends = this.selectedFriends.filter(
        (friend) => friend.id !== friendId
      );
    },
    async sendInvitations() {
      try {
        const wholesalerIds = this.selectedFriends.map(
          (friend) => friend.sender_id
        );
        console.log("Dealership ID:", this.dealershipId);
        console.log("Appraisal ID:", this.appraisalId);
        console.log("Invited Wholesalers IDs:", wholesalerIds);

        const response = await axiosInstance.post(
          endpoints.inviteWholesaler(this.appraisalId),
          { wholesalers: wholesalerIds }
        );

        console.log("Response from server:", response.data);

        this.invitedWholesalers = this.selectedFriends;
        this.selectedFriends = []; // Clear selected friends after sending invitations
      } catch (error) {
        console.error("Error sending invitations:", error);
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString() + " " + date.toLocaleTimeString();
    },
  },
};
</script>

<style scoped>
.offers-container {
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.search-container {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-results {
  margin-top: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 20px;
}

.data-table thead {
  background-color: #f4f4f4;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  font-size: 14px;
}

.data-table th {
  font-weight: bold;
}

.data-table tbody tr:hover {
  background-color: #f1f1f1;
}

.add-button,
.remove-button,
.send-button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-button {
  background-color: #eb5a58;
  color: #fff;
  font-size: 14px;
}

.add-button:hover {
  background-color: #f28b82;
}

.remove-button {
  background-color: #eb5a58;
  color: #fff;
  font-size: 12px;
  margin-left: 10px;
}

.remove-button:hover {
  background-color: #f28b82;
}

.send-button {
  margin-top: 20px;
  background-color: #eb5a58;
  color: #fff;
  font-size: 14px;
  margin-left: 10px;
}

.send-button:hover {
  background-color: #f28b82;
}

.titles {
  font-size: 16px;
  font-weight: 400;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 600;
  padding-left: 10px;
}
</style>
