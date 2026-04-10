import { io } from 'socket.io-client'

let socket = null
let socketUrl = ''

const socketOptions = {
  autoConnect: false,
  path: '/socket.io',
  transports: ['websocket', 'polling'],
  withCredentials: true,
}

export const getSocketClient = (api) => {
  if (api === null || api === undefined) {
    return null
  }

  // api='' means same-origin (Apache/Vite proxy handles /socket.io)
  const resolvedUrl = api || window.location.origin

  if (!socket || socketUrl !== resolvedUrl) {
    if (socket) {
      socket.disconnect()
    }

    socketUrl = resolvedUrl
    socket = io(resolvedUrl, socketOptions)
  }

  return socket
}

export const connectSocketClient = (api) => {
  const client = getSocketClient(api)

  if (client && !client.connected) {
    client.connect()
  }

  return client
}

export const disconnectSocketClient = () => {
  if (socket && socket.connected) {
    socket.disconnect()
  }
}