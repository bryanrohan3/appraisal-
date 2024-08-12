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
</style>
