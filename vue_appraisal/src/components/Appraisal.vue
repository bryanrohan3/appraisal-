<template>
  <div class="appraisal-container">
    <div class="columns-container">
      <div class="column column-60">
        <div class="greetings-container">
          <slot name="header"></slot>
          <form class="customer-details-form">
            <slot name="customer-details"></slot>
          </form>
        </div>
      </div>

      <div class="column column-40">
        <div class="profile-container">
          <slot name="profile"></slot>
        </div>
      </div>
    </div>

    <div class="appraisals-container">
      <div class="appraisals">
        <slot name="basic-vehicle-details"></slot>
      </div>

      <div class="stats-container">
        <div class="stats other-stats">
          <slot name="advanced-vehicle-details"></slot>
        </div>
      </div>
    </div>

    <div class="appraisals-container">
      <div class="appraisals">
        <slot name="vehicle-damages"></slot>
      </div>

      <div class="appraisals-photos">
        <slot name="car-pictures"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Appraisal",
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

.checkbox-and-button {
  display: flex;
  align-items: center;
}

.checkbox-container {
  display: flex;
  align-items: center;
  margin-right: 20px; /* Space between checkbox and button */
}

.checkbox-container input[type="checkbox"] {
  margin-right: 10px; /* Space between checkbox and label */
}

.checkbox-label {
  font-size: 14px; /* Adjust font size as needed */
  font-weight: 400;
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

.appraisals-photos {
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

.appraisals-photos {
  background-color: #ffffff;
  padding: 10px;
  box-sizing: border-box;
  border-radius: 10px;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
  height: 100%; /* Adjust height as necessary */
  position: relative;
}

#photo-upload {
  margin-bottom: 10px;
}

.photos-preview {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
  padding-left: 10px;
}

.photo-container {
  position: relative;
  width: 100px; /* Adjust size as needed */
  height: 100px; /* Adjust size as needed */
  overflow: hidden;
  border-radius: 5px;
}

.photo-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  margin-bottom: 10px;
}

.photo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e7e7e7;
  color: #ffffff;
  font-size: 24px;
  font-weight: bold;
}

.more-photos {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  color: #ffffff;
  border-radius: 5px;
  padding: 5px;
  font-size: 14px;
}

.upload-button {
  padding: 10px;
  font-size: 14px;
}

.add-damage-button {
  width: 30px; /* Size of the button */
  height: 30px; /* Size of the button */
  border-radius: 50%; /* Makes the button circular */
  background-color: #f26764; /* Button background color */
  border: none; /* Remove default border */
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-right: 10px;
}

.add-damage-button img {
  width: 20px; /* Size of the icon */
  height: 20px; /* Size of the icon */
}

.info-text {
  margin: 10px 0;
  font-size: 14px;
  text-align: center;
}

.input {
  width: calc(100% - 22px); /* Adjust based on your design */
}

.damages-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px; /* Adjust as needed */
}

.remove-damage-button {
  background-color: #f26764; /* Button background color */
  border: none; /* Remove default border */
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 10px;
  margin-right: 10px;
  border-radius: 10px;
  margin-left: 10px;
  color: #ffffff;
  margin-bottom: 10px;
  font-weight: 500;
}

.small-header {
  font-size: 12px;
  color: #7d7b7b;
  padding-left: 10px;
  margin-top: 0;
  font-weight: 600;
}

.reserve-price-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  width: 100%; /* Ensure the container takes full width */
}

.reserve-input-wrapper {
  position: relative;
  width: 100%; /* Ensure the wrapper takes full width */
}

.reserve-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none; /* Prevents the icon from blocking input interaction */
  color: #000; /* Adjust the color as needed */
  font-size: 14px; /* Adjust the size as needed */
}

.reserve-input {
  width: 100%;
  padding-left: 30px; /* Add padding to make space for the icon */
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
  height: 39px;
  margin-left: 30px;
  margin-right: 10px;
}

/* Specific styling for reserve input to override generic input styles */
input.reserve-input {
  width: calc(95% - 20px); /* Adjust width to account for padding */
  padding-right: 10px;
  height: 39px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
}

.damage-label {
  padding-left: 10px;
  font-weight: 600;
  color: #7d7b7b;
}

.error-message {
  color: red;
  font-size: 11px;
}
</style>
