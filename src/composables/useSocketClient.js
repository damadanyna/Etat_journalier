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
  if (!api) {
    return null
  }

  if (!socket || socketUrl !== api) {
    if (socket) {
      socket.disconnect()
    }

    socketUrl = api
    socket = io(api, socketOptions)
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