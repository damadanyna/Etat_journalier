export async function safeReadJson(response) {
  const rawBody = await response.text()

  if (!rawBody) {
    return {}
  }

  try {
    return JSON.parse(rawBody)
  } catch {
    return {}
  }
}