<!-- Template -->
<template>
  <div class="split left">
    <div class="login">
      <h2>Welcome back.</h2>
      <p class="welcome-message">Please enter your details to sign in.</p>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username"><b>Username</b></label>
          <input v-model="username" type="text" id="username" required />
        </div>

        <div class="form-group password-input-container">
          <label for="password"><b>Password</b></label>
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            id="password"
            required
          />
          <span class="toggle-password" @click="showPassword = !showPassword">
            <svg
              v-if="showPassword"
              xmlns="http://www.w3.org/2000/svg"
              height="24px"
              viewBox="0 -960 960 960"
              width="24px"
              fill="#e8eaed"
            >
              <path
                d="M644-428-58-58q9-47-27-88t-93-32l-58-58q17-8 34.5-12t37.5-4q75 0 127.5 52.5T660-500q0 20-4 37.5T644-428Zm128 126-58-56q38-29 67.5-63.5T832-500q-50-101-143.5-160.5T480-720q-29 0-57 4t-55 12l-62-62q41-17 84-25.5t90-8.5q151 0 269 83.5T920-500q-23 59-60.5 109.5T772-302Zm20 246L624-222q-35 11-70.5 16.5T480-200q-151 0-269-83.5T40-500q21-53 53-98.5t73-81.5L56-792l56-56 736 736-56 56ZM222-624q-29 26-53 57t-41 67q50 101 143.5 160.5T480-280q20 0 39-2.5t39-5.5l-36-38q-11 3-21 4.5t-21 1.5q-75 0-127.5-52.5T300-500q0-11 1.5-21t4.5-21l-84-82Zm319 93Zm-151 75Z"
              />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              height="24px"
              viewBox="0 -960 960 960"
              width="24px"
              fill="#e8eaed"
            >
              <path
                d="M480-320q75 0 127.5-52.5T660-500q0-75-52.5-127.5T480-680q-75 0-127.5 52.5T300-500q0 75 52.5 127.5T480-320Zm0-72q-45 0-76.5-31.5T372-500q0-45 31.5-76.5T480-608q45 0 76.5 31.5T588-500q0 45-31.5 76.5T480-392Zm0 192q-146 0-266-81.5T40-500q54-137 174-218.5T480-800q146 0 266 81.5T920-500q-54 137-174 218.5T480-200Zm0-300Zm0 220q113 0 207.5-59.5T832-500q-50-101-144.5-160.5T480-720q-113 0-207.5 59.5T128-500q50 101 144.5 160.5T480-280Z"
              />
            </svg>
          </span>
          <!-- </div> -->
        </div>

        <p class="forgot-password">
          <a href="#" class="forgot-password-link">Forgot Password?</a>
        </p>

        <button type="submit">Sign in</button>
      </form>
      <p v-if="errorMessage">{{ errorMessage }}</p>
      <p class="signup-link-p">
        Don't have an account yet?
        <a href="/signup" class="signup-link">Sign up</a>
      </p>
    </div>
  </div>

  <div class="split right">
    <div class="centered">
      <img class="car" src="../../assets/login-screen-car.avif" />
    </div>
  </div>
</template>

<!-- Script -->
<script>
import axios from "axios";
import { mapMutations } from "vuex";
// import { axiosInstance, endpoints } from "@/api/axiosHelper";

export default {
  name: "LogInPage",
  data() {
    return {
      username: "",
      password: "",
      errorMessage: "",
      showPassword: false,
    };
  },
};
</script>

<!-- Styling -->
<style scoped>
.split {
  height: 100vh; /* Ensure full viewport height */
  width: 50vw; /* Ensure half the viewport width */
  position: fixed;
  top: 0;
  z-index: 1;
  overflow: hidden;
  padding: 0; /* Remove any extra padding */
}

.left {
  left: 0;
}

.right {
  right: 0;
  display: flex; /* Use flexbox for centering */
  align-items: center; /* Center vertically */
  justify-content: center; /* Center horizontally */
}

.centered {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.car {
  width: 100vw;
  height: auto;
  max-width: 100vw; /* Ensure the image does not exceed the container width */
  max-height: 100vh; /* Ensure the image does not exceed the viewport height */
}

.split.left {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; /* Ensures it takes the full height of the viewport */
}

.login {
  width: 100%;
  max-width: 400px; /* Ensure the width doesn't exceed this value */
  padding: 2rem;
  background-color: #fff;
  border-radius: 20px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.forgot-password-link {
  text-decoration: none;
  font-weight: bold;
  color: #27282a;
  margin-bottom: 1rem; /* Added margin to separate from the sign-in button */
}

.form-group {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

label {
  margin-bottom: 0.25rem;
  align-self: flex-start;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 0.75rem;
  box-sizing: border-box;
  border: 1px solid #ececec;
  border-radius: 10px;
}

button {
  padding: 0.85rem 1rem;
  background-color: #27282a;
  color: #fff;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
  width: 100%;
  border-radius: 10px;
}

h2 {
  font-family: Arial, sans-serif;
  font-size: 24px;
  margin-bottom: 1.5rem;
}

.signup-link {
  text-decoration: none;
  font-weight: bold;
  color: #27282a;
}

.signup-link-p {
  margin-top: 30px;
}

@media (max-width: 600px) {
  .login {
    margin: 20px;
    padding: 1rem;
    max-width: 90%;
  }

  h2 {
    font-size: 20px;
  }

  button {
    padding: 0.5rem;
  }

  .password-input-container {
    position: relative;
  }

  .password-input-wrapper input[type="password"] {
    padding-right: 40px;
  }

  .toggle-password {
    position: absolute;
    top: 50%;
    right: 10px;
    transform: translateY(-50%);
    cursor: pointer;
  }
}
</style>
