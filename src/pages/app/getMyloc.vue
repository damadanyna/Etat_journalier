<template>
  <div class="   h-full w-[97vw] sm:w-[95vw] md:w-[97vw] flex flex-col  sm:items-center">
    <v-btn
    class=" fixed top-2 left-2"
  aria-label="Options carte"
  icon="mdi-cog"
  text="option"
        @click="showMapOptions = !showMapOptions"
></v-btn> 
    <div class="map-container">
      <div id="map" ref="mapRef"></div>

      <v-card
        v-show="showMapOptions"
        class="custom-control-panel absolute"
      >
        <v-card-title class="text-sm  pa-4 elevation-1 ">Options de carte</v-card-title>

        <v-card-text>
          <v-select
            v-model="selectedMapType"
            :items="mapTypes"
            label="Type de fond de carte"
            @update:model-value="changeMapLayer"
            variant="outlined"
            density="compact"
          ></v-select>

          <v-slider
            v-model="zoom"
            label="Zoom"
            min="6"
            max="18"
            thumb-label
            @update:model-value="updateZoom"
          ></v-slider>

          <v-switch
            v-model="showMarkers"
            label="Afficher les marqueurs"
            @update:model-value="toggleMarkers"
            color="green-accent-3"
          ></v-switch>
        </v-card-text>

        <v-card-actions>
          <v-btn color="green-accent-3" @click="addRandomMarker">
            Ajouter un marqueur aléatoire
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, onBeforeMount } from 'vue';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Refs
const mapRef = ref(null);
const showMapOptions = ref(false);
const zoom = ref(13);
const selectedMapType = ref('streets');
const showMarkers = ref(true);

// Map types
const mapTypes = [
  { title: 'OpenStreetMap', value: 'streets' },
  { title: 'Satellite', value: 'satellite' },
  { title: 'Terrain', value: 'terrain' }
];

// Leaflet states
let map = null;
let center =[-18.918569, 47.521351];
let baseLayers = {};
let currentBaseLayer = null;
let markers = [];
let markerLayerGroup = null;

let landmarks = [
    { name: 'Banay', coords: [-18.940326, 47.529176] },
    { name: 'Vony', coords: [-18.926906, 47.462353] },
    // { name: 'Notre-Dame', coords: [48.853, 2.3499] }
  ];

const greenIcon = L.icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

onBeforeMount(() => {  
});

onMounted(() => {
  // initMap();
  
  searchAndAddSIPEM()
  setTimeout(async() => {
    try {
      
      const pos = await getCurrentPositionCoords();
      center = pos;
      landmarks.push({ name: 'Ma position', coords: pos });
    } catch (err) {
      console.warn('Position utilisateur non disponible :', err.message);
    } finally {
      initMap(); // Lance la carte même si la position est refusée
    }
    
  console.log("Landmarks mis à jour :", landmarks)
  }, 1000);
  
});

onUnmounted(() => {
  if (map) {
    map.remove();
    map = null;
  }
});

function initMap() {
  map = L.map(mapRef.value).setView(center, zoom.value);

  baseLayers = {
    streets: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }),
    satellite: L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      {
        attribution: 'Imagery &copy; Esri'
      }
    ),
    terrain: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenTopoMap contributors'
    })
  };

  currentBaseLayer = baseLayers[selectedMapType.value];
  currentBaseLayer.addTo(map);

  markerLayerGroup = L.layerGroup().addTo(map);
  addDefaultMarkers();

  map.on('zoomend', () => {
    zoom.value = map.getZoom();
  });
}


async function searchAndAddSIPEM() {
  let array_=[]
  const query = "TOTAL"
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=mg`

  const response = await fetch(url, {
    headers: {
      'User-Agent': 'MyLeafletApp/1.0 (contact@domain.com)'
    }
  })

  const data = await response.json()
  console.log(data);
  

  data.forEach(place => {
    // Si le nom contient bien "SIPEM" (sécurité)
    if (place.display_name.toLowerCase().includes("sipem")) {
      landmarks.push({
        name: place.display_name,
        coords: [parseFloat(place.lat), parseFloat(place.lon)]
      })
    }
  }) 
}
function changeMapLayer() {
  if (currentBaseLayer) {
    map.removeLayer(currentBaseLayer);
  }
  currentBaseLayer = baseLayers[selectedMapType.value];
  currentBaseLayer.addTo(map);
}

function updateZoom() {
  map.setZoom(zoom.value);
}

function addDefaultMarkers() {


  landmarks.forEach(landmark => {
    const marker = L.marker(landmark.coords,{ icon: greenIcon }).bindPopup(markerClickHandler(landmark.name,'20%'));
    // const marker = L.marker(landmark.coords).bindPopup(`<b>${landmark.name}</b>`);
    markers.push(marker);
    markerLayerGroup.addLayer(marker);
  });
}

function markerClickHandler(name,precentage) {
  // const marker = e.target;
  // marker.openPopup();
  return `<div class="font-bold ">
    <div class="  text-green text-lg ">${name}</div>
    <div class="">Vente : ${precentage}</div>  
    </div>`
}

function toggleMarkers() {
  if (showMarkers.value) {
    markerLayerGroup.addTo(map);
  } else {
    map.removeLayer(markerLayerGroup);
  }
}

function addRandomMarker() {
  const lat = center[0] + (Math.random() - 0.5) * 0.05;
  const lng = center[1] + (Math.random() - 0.5) * 0.05;

  const marker = L.marker([lat, lng]).bindPopup(
    `<b>Point ${markers.length + 1}</b><br>Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}`
  );

  markers.push(marker);
  markerLayerGroup.addLayer(marker);

  if (!showMarkers.value) {
    showMarkers.value = true;
    markerLayerGroup.addTo(map);
  }

  map.setView([lat, lng], zoom.value);
}

function getCurrentPositionCoords() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('La géolocalisation n’est pas supportée par ce navigateur.'));
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords = position.coords;
        resolve([coords.latitude, coords.longitude]);
      },
      (error) => {
        reject(new Error(`Erreur de géolocalisation : ${error.message}`));
      }
    );
  });
}
 

</script>

<style scoped>
.map-container {
  height: 85%;
  width: 85%;
  position: relative;
}

#map {
  height: 100%;
  width: 100%;
  z-index: 1;
}

.custom-control-panel {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 1000;
  max-width: 320px;
}
</style>
