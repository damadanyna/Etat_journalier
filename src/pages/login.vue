<template>
  <div class="login-page">
    <div class="login-card">
      <!-- Left side illustration -->
      <div class="login-left" >
        <img src="data:image/jpeg;base64,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" alt="Rocket" class="illustration" />
        <p class="description">
            Tout  en <br />
            quelques minutes seulement. <strong>Baiboho</strong>
        </p>
      </div>

      <!-- Right side login form -->
      <div class="login-right">
        <div class="tabs">
          <button :class="{ active: activeTab === 'signIn' }" @click="activeTab = 'signIn'">Se connecter</button>
          <button :class="{ active: activeTab === 'signUp' }" @click="activeTab = 'signUp'">S'inscrire</button>
        </div>

        <h2>{{ activeTab === 'signIn' ? 'Connexion' : 'Inscription' }}</h2>

        <form @submit.prevent="handleSubmit">
          <input type="text" placeholder="Votre nom d'utilisateur" v-model="username" />
          <input type="password" placeholder="Mot de passe" v-model="password" />
          <input v-if="activeTab !== 'signIn'" type="Verification mot de passe" placeholder="Verification mot de passe" v-model="verif_password" />
          <input v-if="activeTab !== 'signIn'"  type="text" placeholder="Immatricule" v-model="immatricule" />
          <a href="#" v-if="activeTab === 'signIn'" class="forgot">Mot de passe oublier?</a>
          <button type="submit">{{ activeTab === 'signIn' ? 'Connexion' : 'Inscription' }}</button>
        </form>

        <div class="social-login"  v-if="activeTab === 'signIn'">
          <button class="google">G</button>
          <button class="facebook">F</button>
          <button class="twitter">T</button>
          <button class="github">GH</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"

const activeTab = ref("signIn") // par défaut "Connexion"
const username = ref("")
const password = ref("")
const verif_password = ref("")
const immatricule = ref("")
const errorMessage = ref("")

const handleSubmit = async () => {    
  try {
    console.log(activeTab.value)
    if (activeTab.value === "signIn") {
          // ---- Connexion ----
        const formData = new FormData();
        formData.append("username", username.value);
        formData.append("password", password.value);

        const response = await fetch("http://192.168.1.212:8000/api/signin", {
          method: "POST",
          body: formData
        });

        if (!response.ok) throw new Error("Identifiants invalides");

        const data = await response.json();

        // ✅ Stocker le token dans le localStorage
        if (data.access_token) {
          localStorage.setItem("access_token", data.access_token);
          alert(`Bienvenue ${data.user.username} !`);
        } else {
          console.error("Token manquant dans la réponse");
        }

    } else {
      // ---- Inscription ----
        if (password.value !== verif_password.value) {
          throw new Error("Les mots de passe ne correspondent pas")
        } 
        const formData = new FormData()
        formData.append("username", username.value)
        formData.append("password", password.value)
        formData.append("immatricule", immatricule.value)

        const response = await fetch("http://192.168.1.212:8000/api/signup", {
            method: "POST",  
            body:  formData,
            credentials: "include"
        })
      

      if (!response.ok) throw new Error("Erreur lors de l'inscription")
      const data = await response.json()
      alert(`Utilisateur ${data.username} inscrit avec succès !`)
    }
  } catch (err) {
    errorMessage.value = err.message
  }
}
</script>



<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #4e6555, #29683e);
  font-family: 'Poppins', sans-serif;
}

.login-card {
  display: flex;
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(15px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
  background: rgba(255,255,255,0.05);
  width: 900px;
  height: 60vh;
  max-width: 90%;
}

.login-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  background: rgb(255, 255, 255);
  color: black;
  text-align: center;
  border-radius:0px 160px 160px 0px;
}

.login-left .illustration {
  width: 150px;
  margin-bottom: 20px;
}

.login-left .description {
  font-size: 1rem;
  line-height: 1.5;
}

.login-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px;
  color: #fff;
}

.tabs {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.tabs button {
  background: transparent;
  border: none;
  color: #fff;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 500;
  border-radius: 10px;
  transition: background 0.3s;
}

.tabs button.active {
  background: rgba(255,255,255,0.2);
}

.login-right h2 {
  margin-bottom: 20px;
  font-size: 1.8rem;
}

.login-right form {
  display: flex;
  flex-direction: column;
}

.login-right input {
  margin-bottom: 15px;
  padding: 12px 15px;
  border-radius: 10px;
  border: none;
  outline: none;
  background: rgba(255,255,255,0.15);
  color: #fff;
  font-size: 1rem;
}

.login-right .forgot {
  align-self: flex-end;
  margin-bottom: 15px;
  font-size: 0.9rem;
  color: #ccc;
  text-decoration: underline;
}

.login-right button[type="submit"] {
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: #1a1a2e;
  color: #fff;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s;
}

.login-right button[type="submit"]:hover {
  background: #da2323cf; 
}

.social-login {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  gap: 15px;
}

.social-login button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,0.2);
  color: #fff;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}

.social-login button:hover {
  background: rgba(255,255,255,0.4);
}
</style>
