export function useActivityLogger(api) {
  const logUserActivity = async ({
    action,
    entityType,
    entityId = '',
    description = '',
    status = 'SUCCESS',
  }) => {
    const token = localStorage.getItem('access_token')

    if (!token || !api || !action || !entityType) {
      return false
    }

    try {
      const formData = new FormData()
      formData.append('action', action)
      formData.append('entity_type', entityType)
      formData.append('entity_id', entityId)
      formData.append('description', description)
      formData.append('status', status)

      const response = await fetch(`${api}/api/log_user_activity`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      return response.ok
    } catch (error) {
      console.error('Erreur de journalisation activité :', error)
      return false
    }
  }

  return { logUserActivity }
}