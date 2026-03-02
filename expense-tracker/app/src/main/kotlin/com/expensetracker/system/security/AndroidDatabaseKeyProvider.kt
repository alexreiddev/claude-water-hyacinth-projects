@file:Suppress("ktlint:standard:no-empty-file")

package com.expensetracker.system.security

// ANDROID-ONLY — This file requires the Android Gradle plugin, BiometricPrompt, and AndroidKeyStore.
// Uncomment the class body when migrating.
//
// import android.security.keystore.KeyGenParameterSpec
// import android.security.keystore.KeyProperties
// import java.security.KeyStore
// import javax.crypto.KeyGenerator
// import javax.crypto.SecretKey
//
// /**
//  * Production [DatabaseKeyProvider] backed by the Android Keystore system.
//  *
//  * The AES-256 key is generated inside the TEE (Trusted Execution Environment) or StrongBox
//  * hardware security module when available. The raw key material **never leaves the hardware**;
//  * only the encoded form used by SQLCipher's `SupportFactory` is returned.
//  *
//  * ## Biometric gating (optional hardening)
//  * To require biometric authentication before the key can be used, add
//  * `setUserAuthenticationRequired(true)` to [KeyGenParameterSpec.Builder] and call
//  * [android.hardware.biometrics.BiometricPrompt] before opening the database.
//  * This is enforced by the OS — no application-layer code can bypass it.
//  *
//  * ## Key rotation
//  * To rotate the key (e.g., after a security event), delete the existing alias
//  * via `KeyStore.deleteEntry(KEY_ALIAS)` and call [getDatabaseKey] again.
//  * The database must be re-encrypted with the new key using SQLCipher's `sqlcipher_export`.
//  */
// class AndroidDatabaseKeyProvider : DatabaseKeyProvider {
//
//     private companion object {
//         const val KEY_ALIAS = "expense_tracker_db_key"
//         const val ANDROID_KEYSTORE = "AndroidKeyStore"
//     }
//
//     override fun getDatabaseKey(): ByteArray {
//         val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).also { it.load(null) }
//         val existingKey = keyStore.getKey(KEY_ALIAS, null) as? SecretKey
//         return (existingKey ?: generateAndStoreKey()).encoded
//     }
//
//     private fun generateAndStoreKey(): SecretKey {
//         val spec = KeyGenParameterSpec.Builder(
//             KEY_ALIAS,
//             KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
//         )
//             .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
//             .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
//             .setKeySize(256)
//             .setIsStrongBoxBacked(true) // falls back to TEE if StrongBox unavailable
//             // Uncomment to gate key use on biometric authentication:
//             // .setUserAuthenticationRequired(true)
//             // .setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG)
//             .build()
//
//         val keyGen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE)
//         keyGen.init(spec)
//         return keyGen.generateKey()
//     }
// }
