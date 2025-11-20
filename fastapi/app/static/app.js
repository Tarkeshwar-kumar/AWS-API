async function fetchJson(url) {
  const r = await fetch(url)
  return r.json()
}

document.getElementById('btn-buckets').addEventListener('click', async () => {
  const area = document.getElementById('buckets-area')
  area.innerHTML = 'Loading...'
  try {
    const data = await fetchJson('/api/buckets')
    if (!data.ok) throw new Error(data.error || 'Unknown')
    if (data.buckets.length === 0) {
      area.innerHTML = '<em>No buckets found</em>'
      return
    }
    const rows = data.buckets.map(b => `<tr><td>${b.Name}</td><td>${b.CreationDate}</td></tr>`).join('')
    area.innerHTML = `<table><thead><tr><th>Name</th><th>CreationDate</th></tr></thead><tbody>${rows}</tbody></table>`
  } catch (err) {
    area.innerHTML = `<pre>${err.message}</pre>`
  }
})

document.getElementById('btn-ec2').addEventListener('click', async () => {
  const area = document.getElementById('ec2-area')
  const region = document.getElementById('region').value
  area.innerHTML = 'Loading...'
  try {
    const data = await fetchJson(`/api/ec2?region=${region}`)
    if (!data.ok) throw new Error(data.error || 'Unknown')
    if (data.instances.length === 0) {
      area.innerHTML = '<em>No instances found</em>'
      return
    }
    const rows = data.instances.map(i => `<tr><td>${i.InstanceId}</td><td>${i.State}</td><td>${i.InstanceType}</td><td>${i.PublicIpAddress||''}</td><td>${i.PrivateIpAddress||''}</td></tr>`).join('')
    area.innerHTML = `<table><thead><tr><th>ID</th><th>State</th><th>Type</th><th>Public IP</th><th>Private IP</th></tr></thead><tbody>${rows}</tbody></table>`
  } catch (err) {
    area.innerHTML = `<pre>${err.message}</pre>`
  }
})