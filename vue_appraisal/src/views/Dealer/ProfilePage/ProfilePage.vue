<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Profile Page</h1>
      <div class="notification-button" @click="saveProfile">
        <span class="button-text">Save</span>
      </div>
    </div>

    <div v-if="profile" class="columns-container">
      <div class="column column-60">
        <form class="customer-details-form">
          <div class="form-row-horizontal">
            <div class="form-group">
              <label for="firstName">First Name</label>
              <input
                id="firstName"
                type="text"
                v-model="profile.user.first_name"
              />
            </div>
            <div class="form-group">
              <label for="lastName">Last Name</label>
              <input
                id="lastName"
                type="text"
                v-model="profile.user.last_name"
              />
            </div>
          </div>

          <div class="form-row-horizontal">
            <div class="form-group">
              <label for="email">Username</label>
              <input
                id="username"
                type="text"
                v-model="profile.user.username"
              />
            </div>
            <div class="form-group">
              <label for="email">Email</label>
              <input id="email" type="text" v-model="profile.user.email" />
            </div>
          </div>

          <div class="form-row-horizontal">
            <div class="form-group">
              <label for="phone">Phone Number</label>
              <input id="phone" type="text" v-model="profile.phone" />
            </div>
            <div class="form-group">
              <label for="role">Role</label>
              <input id="role" type="text" :value="formattedRole" disabled />
            </div>
          </div>
          <div class="form-row">
            <label for="dealerships">Dealerships</label>
            <table class="appraisals-table">
              <tbody>
                <tr
                  v-for="(dealership, index) in profile.dealership_names"
                  :key="index"
                >
                  <td>
                    <img class="car" src="@/assets/car.svg" alt="car" />
                    {{ dealership.dealership_name }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </form>
      </div>
    </div>

    <div
      v-if="profile && profile.role === 'M'"
      class="delete-account-container"
    >
      <div class="delete-account-icon">
        <img src="@/assets/error.svg" alt="Error" />
      </div>
      <div class="delete-account-content">
        <p><strong>Delete Account</strong></p>
        <p>
          After making a deletion request, you will have
          <strong>6 months</strong> to maintain this account.
        </p>
        <button class="delete-account-button" @click="confirmDeleteAccount">
          Delete My Account
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { endpoints, axiosInstance } from "@/helpers/axiosHelper";
import { mapMutations } from "vuex";

export default {
  name: "ProfilePage",
  data() {
    return {
      profile: null,
    };
  },
  computed: {
    dealershipsString() {
      return this.profile.dealership_names
        .map((d) => d.dealership_name)
        .join(", ");
    },
    formattedRole() {
      return this.profile.role === "M"
        ? "Management"
        : this.profile.role === "S"
        ? "Sales"
        : "Unknown";
    },
  },
  async created() {
    try {
      const response = await axiosInstance.get(endpoints.dealerProfile);
      this.profile = response.data;
      console.log("Profile data:", this.profile); // Log the profile data
    } catch (error) {
      console.error("Error fetching profile:", error);
    }
  },
  methods: {
    ...mapMutations(["logout"]),
    async saveProfile() {
      try {
        const userId = this.profile.user.id;

        // Ensure dealerProfileId is correctly set from the profile
        const dealerProfileId = this.profile.id; // Adjust according to the actual key

        if (!dealerProfileId) {
          throw new Error("Dealer Profile ID is missing.");
        }

        // Prepare the data for updating the phone number
        const phoneUpdateData = {
          phone: this.profile.phone,
        };

        // Prepare the data for updating other fields
        const userUpdateData = {
          first_name: this.profile.user.first_name,
          last_name: this.profile.user.last_name,
          email: this.profile.user.email,
          username: this.profile.user.username,
        };

        // Update phone number
        await axiosInstance.patch(
          endpoints.dealerProfileUpdate(dealerProfileId),
          phoneUpdateData
        );

        // Update other user details
        await axiosInstance.patch(endpoints.updateUser(userId), userUpdateData);

        console.log("Profile updated successfully");
      } catch (error) {
        console.error("Error updating profile:", error);
      }
    },

    confirmDeleteAccount() {
      // Show confirmation dialog
      const confirmed = confirm(
        "Are you sure you want to delete your account? This action cannot be undone."
      );
      if (confirmed) {
        this.handleDeleteAccount();
      }
    },

    async handleDeleteAccount() {
      try {
        const response = await axiosInstance.patch(endpoints.deleteCurrentUser);
        this.logout();
        console.log("Profile deleted successfully:", response.data);

        // Redirect to login page after successful deletion
        this.$router.push({ name: "login" });
      } catch (error) {
        console.error("Error deleting profile:", error);
      }
    },
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

.columns-container {
  display: flex;
  margin: 20px 0;
  gap: 20px;
}

.column {
  padding: 20px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  transition: 0.3s;
}

.column-60 {
  width: 100%;
  background-color: #ffffff;
}

.customer-details-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.form-row label {
  margin-bottom: 10px;
  font-size: 12px;
  color: #7d7b7b;
  margin-top: 0;
  font-weight: 600;
}

.form-row-horizontal label {
  margin-bottom: 10px;
  font-size: 12px;
  color: #7d7b7b;
  margin-top: 0;
  font-weight: 600;
}

input[type="text"],
input[type="password"],
input[type="email"],
select {
  width: 100%;
  padding: 10px;
  margin-bottom: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
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

/* Table Styling */
.appraisals-table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

.appraisals-table th,
.appraisals-table td {
  text-align: left;
  padding: 8px;
  font-size: 14px;
}

.appraisals-table th {
  font-weight: 600;
  background-color: #aaa;
  color: #fff;
}

.appraisals-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.appraisals-table-header {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-size: 14px;
  color: #fff;
}

.button-text {
  padding: 0 10px; /* Adjust padding as needed */
}

.notification-button {
  width: 150px; /* Adjust width to fit text */
  height: 40px;
  border-radius: 20px; /* Rounded corners for button */
  background-color: #eb5a58;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px; /* Adjust font size */
  font-weight: 600;
  color: #ffffff; /* Text color */
  text-align: center;
  border: 4px solid white;
  border-radius: 50px;
}

.car {
  width: 20px; /* Keep the car size */
  margin-right: 10px; /* Keep spacing between the image and the dealership name */
  vertical-align: middle; /* Align the car image with the middle of the text */
  padding-bottom: 3px;
}

/* Delete Account Button */
.delete-account-container {
  display: flex;
  align-items: center;
  margin-top: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.delete-account-icon {
  flex-shrink: 0;
  margin-right: 20px;
}

.delete-account-icon img {
  width: 40px; /* Adjust size as needed */
  height: 40px;
}

.delete-account-content {
  flex-grow: 1;
}

.delete-account-content p {
  margin: 0;
  font-size: 14px;
  padding: 5px 0 5px 0;
  color: #6c757d;
}

.delete-account-content strong {
  font-size: 16px;
  color: #343a40;
}

.delete-account-button {
  margin-top: 10px;
  padding: 10px 20px;
  background-color: #eb5a58;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s ease;
}

.delete-account-button:hover {
  background-color: #d9534f;
}
</style>
