package com.expensetracker.system.security

/**
 * Provides the encryption key used to open the SQLCipher-encrypted Room database.
 *
 * The key is a 32-byte (256-bit) AES secret. Implementations must:
 * - Generate and securely persist the key on first call.
 * - Return the same key on subsequent calls (key must be stable across process restarts).
 * - Never log or expose the raw key bytes.
 *
 * ## Platform implementations
 *
 * | Environment | Implementation | Key storage |
 * |---|---|---|
 * | JVM (tests / CI) | [JvmDatabaseKeyProvider] | JDK PKCS12 `KeyStore` file |
 * | Android (production) | `AndroidDatabaseKeyProvider` (see `system/security/`) | `AndroidKeyStore` TEE / StrongBox |
 *
 * ## Android migration note
 * On Android the key should never leave the `AndroidKeyStore` hardware boundary.
 * `SupportFactory` accepts a passphrase (byte array) derived from the key — ensure
 * the byte array is zeroed after use:
 * ```kotlin
 * val passphrase = keyProvider.getDatabaseKey()
 * try {
 *     SupportFactory(passphrase)
 * } finally {
 *     passphrase.fill(0)
 * }
 * ```
 */
interface DatabaseKeyProvider {
    /**
     * Returns the 32-byte AES database key, generating and persisting it if this is the first call.
     *
     * @throws SecurityException if the key cannot be generated or retrieved.
     */
    fun getDatabaseKey(): ByteArray
}
