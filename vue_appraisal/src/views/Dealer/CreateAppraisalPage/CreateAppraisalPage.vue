<template>
  <div class="dashboard-container">
    <div class="title-container">
      <h1 class="title">Create Appraisal Form</h1>
      <div class="notification-button">
        <span class="button-text">Create Appraisal</span>
      </div>
    </div>
    <div class="columns-container">
      <div class="column column-60">
        <div class="greetings-container">
          <p class="headers">Customer Personal Details</p>
          <form class="customer-details-form">
            <div class="form-row">
              <input type="text" placeholder="First Name" />
              <input type="text" placeholder="Last Name" />
            </div>
            <div class="form-row">
              <input type="email" placeholder="Email" />
              <div class="phone-input">
                <select>
                  <option
                    v-for="(code, country) in phoneCodes"
                    :key="code"
                    :value="code"
                  >
                    {{ code }} ({{ country }})
                  </option>
                </select>
                <input type="text" placeholder="Phone" />
              </div>
            </div>
          </form>
        </div>
      </div>

      <div class="column column-40">
        <div class="profile-container">
          <div class="profile-picture"></div>
          <p class="name">{{ userName }}</p>
          <p class="email">{{ userEmail }}</p>
          <div class="dealership-dropdown">
            <select class="input-dealership" v-model="selectedDealership">
              <option
                v-for="option in dealershipOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="appraisals-container">
      <div class="appraisals">
        <p class="headers">Basic Vehicle Details</p>
        <input type="text" placeholder="Vehicle Make" class="input" />
        <input type="text" placeholder="Vehicle Model" class="input" />
        <input type="text" placeholder="Vehicle Year" class="input" />
        <input type="text" placeholder="Vehicle Colour" class="input" />
        <input
          type="text"
          placeholder="Vehicle Registration Number"
          class="input"
        />
      </div>

      <div class="stats-container">
        <div class="stats other-stats">
          <p class="headers">Advanced Vehicle Details</p>
          <input type="text" placeholder="Odometer Reading" class="input" />
          <input type="text" placeholder="Engine Type" class="input" />
          <select class="input">
            <option
              v-for="option in transmissionOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
          <select class="input">
            <option
              v-for="option in fuelOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
          <input type="text" placeholder="Body Type" class="input" />
          <input type="text" placeholder="Reserve Price" class="input" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";
import { axiosInstance, endpoints } from "@/helpers/axiosHelper";

export default {
  name: "CreateAppraisalPage",
  computed: {
    ...mapGetters(["getUserProfile"]),
    userName() {
      const userProfile = this.getUserProfile;
      return userProfile
        ? `${userProfile.first_name} ${userProfile.last_name}`
        : "Guest";
    },
    userEmail() {
      const userProfile = this.getUserProfile;
      return userProfile ? userProfile.email : "";
    },
  },
  data() {
    return {
      showDropdown: false,
      selectedDealership: "",
      dealershipOptions: [
        { value: "", label: "Select Dealership" },
        { value: "0", label: "Pablo's Car Dealership" },
        { value: "1", label: "Riverdale Car Dealership" },
        { value: "2", label: "Bob's Car Dealership" },
      ], // Mock data
      phoneCodes: {
        "+61": "AU",
        "+1": "US",
        "+44": "UK",
      },
      transmissionOptions: [
        { value: "", label: "Transmission" },
        { value: "automatic", label: "Automatic" },
        { value: "manual", label: "Manual" },
      ],
      fuelOptions: [
        { value: "", label: "Fuel Type" },
        { value: "diesel", label: "Diesel" },
        { value: "petrol", label: "Petrol" },
        { value: "electric", label: "Electric" },
        { value: "hybrid", label: "Hybrid" },
      ],
    };
  },
  methods: {
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
    },
    selectDealership(dealership) {
      this.selectedDealership = dealership;
      this.showDropdown = false;
    },
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

.notification-button {
  width: 150px; /* Adjust width to fit text */
  height: 40px;
  border-radius: 20px; /* Rounded corners for button */
  background-color: #f26764;
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

.button-text {
  padding: 0 10px; /* Adjust padding as needed */
}

.title {
  font-size: 24px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 200;
  font-weight: 600;
}

.columns-container {
  display: flex;
  margin: 20px 0;
  gap: 20px;
}

.column {
  padding: 10px;
  box-sizing: border-box;
  height: 210px;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  transition: 0.3s;
}

.column-60 {
  width: 75%;
  background-color: #ffffff;
}

.column-40 {
  width: 25%;
  background-color: #ffffff;
}

.profile-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 10px;
  margin: 0;
  font-size: 16px;
  font-weight: 400;
}

.profile-picture {
  height: 70px;
  width: 70px;
  border-radius: 50%;
  background-color: #e7e7e7;
  margin-bottom: 10px;
}

.name {
  margin: 0;
}
.email {
  color: #7d7b7b;
  font-size: 12px;
}

.appraisals-listings {
  width: 75%;
  background-color: #ffffff;
}

.headers {
  font-size: 16px;
  font-weight: 400;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 600;
  padding-left: 10px;
}

.greetings-container {
  width: 100%;
  padding: 10px;
  margin: 0;
}

.customer-details-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-right: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
  width: 100%;
}

.phone-input {
  display: flex;
  gap: 10px;
  width: 100%;
}

.phone-input input[type="text"] {
  width: 70%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
}

/* dealership button */
.dealership-dropdown {
  position: relative;
  display: inline-block;
}

.dealership-dropdown button {
  padding: 8px 16px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 400;
  font-size: 12px;
  border: none;
  border-radius: 5px;
  background-color: #ffffff;
  border: 1px solid #000000;
  color: #000000;
  cursor: pointer;
  width: 100%;
}

.dropdown-content {
  display: block;
  position: absolute;
  background-color: #f9f9f9;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  z-index: 1;
  border-radius: 5px;
  margin-top: 8px;
  width: 100%;
  font-size: 11px;
}

.dropdown-content p {
  color: black;
  padding: 5px;
  text-decoration: none;
  display: block;
  cursor: pointer;
}

.dropdown-content p:hover {
  background-color: #f1f1f1;
}

.input {
  margin-bottom: 20px;
  width: 95%;
  margin-left: 10px;
}

.input-dealership {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  font-weight: 400;
  font-size: 12px;
  border: none;
  border-radius: 5px;
  background-color: #ffffff;
  border: 1px solid #000000;
  width: 100%;
  color: #000000;
  cursor: pointer;
  text-align: center;
}

input[type="text"],
input[type="email"],
select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
  width: 95%;
  height: 39px;
}

input[type="text"],
input[type="email"] {
  /* Ensure these fields have the same height */
  height: 39px; /* Adjust as necessary to match your design */
}

select {
  width: 95%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
  height: 39px;
  -webkit-appearance: none; /* Remove default styles in WebKit browsers */
  -moz-appearance: none; /* Remove default styles in Firefox */
  appearance: none; /* Remove default styles */
  background: white; /* Ensure the background color matches */
}

.appraisals-container {
  display: flex;
  margin: 20px 0;
  gap: 20px;
}

.appraisals {
  width: 50%;
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  height: 100%; /* Make sure the height adjusts with the content */
}

.stats-container {
  width: 50%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%; /* Make sure the height adjusts with the content */
}

.stats {
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  flex: 1; /* Ensure stats containers grow to the same height */
}

.other-stats {
  flex: 1;
}
</style>
