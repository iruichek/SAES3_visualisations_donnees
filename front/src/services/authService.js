import bcrypt from 'bcryptjs'
import comptesDemo from '@/data/comptes-demo.json'

const accountsKey = 'nuage-sur-les-rails:accounts'

function readAccounts() {
  const saved = localStorage.getItem(accountsKey)
  return saved === null ? comptesDemo : JSON.parse(saved)
}

function saveAccounts(accounts) {
  localStorage.setItem(accountsKey, JSON.stringify(accounts))
}

function publicUser({ id, login, role }) {
  return { id, login, role }
}

export async function login({ login, password }) {
  const loginNormalise = login.trim().toLowerCase()
  const account = readAccounts().find((user) => user.login === loginNormalise)

  if (!account || bcrypt.truncates(password) || !(await bcrypt.compare(password, account.passwordHash))) {
    throw new Error('Login ou mot de passe incorrect.')
  }

  return { user: publicUser(account), sessionId: crypto.randomUUID() }
}

export async function register({ login, password }) {
  const loginNormalise = login.trim().toLowerCase()

  if (!loginNormalise) {
    throw new Error('Saisis un login.')
  }

  if (password.length < 8 || bcrypt.truncates(password)) {
    throw new Error('Le mot de passe doit contenir au moins 8 caractères et au plus 72 octets.')
  }

  const passwordHash = await bcrypt.hash(password, 10)
  const accounts = readAccounts()

  if (accounts.some((user) => user.login === loginNormalise)) {
    throw new Error('Ce login est déjà utilisé.')
  }

  const account = {
    id: crypto.randomUUID(),
    login: loginNormalise,
    passwordHash,
    role: 'user',
  }

  saveAccounts([...accounts, account])
}

export function listUsers() {
  return readAccounts().filter((user) => user.role === 'user').map(publicUser)
}

export function deleteUser(id) {
  saveAccounts(readAccounts().filter((user) => user.role !== 'user' || user.id !== id))
}