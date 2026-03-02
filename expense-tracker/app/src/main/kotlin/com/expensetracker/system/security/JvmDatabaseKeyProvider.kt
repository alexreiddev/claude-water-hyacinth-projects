package com.expensetracker.system.security

import java.io.File
import java.security.KeyStore
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey

/**
 * JVM implementation of [DatabaseKeyProvider] using the JDK PKCS12 [KeyStore].
 *
 * On first call the provider generates a 256-bit AES key, stores it in a PKCS12 keystore
 * file at [keystorePath], and returns the raw encoded bytes. Subsequent calls load and
 * return the same key, ensuring the database can be re-opened across JVM restarts.
 *
 * **This implementation is for development and testing only.**
 * The keystore password is passed as a constructor parameter and is not hardware-backed.
 * On Android, replace this with `AndroidDatabaseKeyProvider` which stores the key in the
 * `AndroidKeyStore` TEE and never exposes raw key material to the JVM heap.
 *
 * @param keystorePath Location of the PKCS12 keystore file. Parent directories are created
 *   automatically. Defaults to `~/.expense-tracker/db.ks`.
 * @param keystorePassword Password protecting the keystore. **Change this in any environment
 *   where the keystore file is not itself protected by OS-level access controls.**
 */
class JvmDatabaseKeyProvider(
    private val keystorePath: File =
        File(System.getProperty("user.home"), ".expense-tracker/db.ks"),
    private val keystorePassword: CharArray = "changeme-in-production".toCharArray(),
) : DatabaseKeyProvider {
    private companion object {
        const val KEY_ALIAS = "expense-tracker-db-key"
        const val KEY_ALGORITHM = "AES"
        const val KEY_SIZE_BITS = 256
        const val KEYSTORE_TYPE = "PKCS12"
    }

    override fun getDatabaseKey(): ByteArray {
        val keyStore = loadOrCreateKeyStore()
        val existingKey = keyStore.getKey(KEY_ALIAS, keystorePassword) as? SecretKey
        if (existingKey != null) {
            return existingKey.encoded
        }
        val newKey = generateAesKey()
        storeKey(keyStore, newKey)
        return newKey.encoded
    }

    private fun loadOrCreateKeyStore(): KeyStore {
        val ks = KeyStore.getInstance(KEYSTORE_TYPE)
        if (keystorePath.exists()) {
            keystorePath.inputStream().use { stream ->
                ks.load(stream, keystorePassword)
            }
        } else {
            ks.load(null, keystorePassword)
        }
        return ks
    }

    private fun generateAesKey(): SecretKey {
        val keyGen = KeyGenerator.getInstance(KEY_ALGORITHM)
        keyGen.init(KEY_SIZE_BITS)
        return keyGen.generateKey()
    }

    private fun storeKey(
        keyStore: KeyStore,
        key: SecretKey,
    ) {
        keyStore.setKeyEntry(KEY_ALIAS, key, keystorePassword, null)
        keystorePath.parentFile?.mkdirs()
        keystorePath.outputStream().use { stream ->
            keyStore.store(stream, keystorePassword)
        }
    }
}
