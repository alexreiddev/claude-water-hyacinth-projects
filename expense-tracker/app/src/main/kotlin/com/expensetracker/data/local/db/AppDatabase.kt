@file:Suppress("ktlint:standard:no-empty-file")

package com.expensetracker.data.local.db

// ANDROID-ONLY — This file requires the Android Gradle plugin, Room, and SQLCipher.
// Uncomment the class body when migrating.
//
// import android.content.Context
// import androidx.room.Database
// import androidx.room.Room
// import androidx.room.RoomDatabase
// import androidx.sqlite.db.SupportSQLiteDatabase
// import com.expensetracker.data.local.dao.RoomCategoryDao
// import com.expensetracker.data.local.dao.RoomMerchantDao
// import com.expensetracker.data.local.dao.RoomTransactionDao
// import com.expensetracker.data.local.entity.CategoryEntity
// import com.expensetracker.data.local.entity.MerchantEntity
// import com.expensetracker.data.local.entity.TransactionEntity
// import com.expensetracker.system.security.DatabaseKeyProvider
// import net.zetetic.database.sqlcipher.SupportFactory
//
// /**
//  * Room database definition for the expense tracker.
//  *
//  * ## SQLCipher encryption
//  * The database file is encrypted at rest using SQLCipher 4. The 256-bit AES key is
//  * provided by [DatabaseKeyProvider] and passed to [SupportFactory]. The key is sourced
//  * from the Android Keystore via `AndroidDatabaseKeyProvider` — it never leaves hardware.
//  *
//  * ## Schema version history
//  * | Version | Description |
//  * |---|---|
//  * | 1 | Initial schema: transactions, merchants, categories |
//  *
//  * ## Usage
//  * Obtain an instance via Hilt injection (see [com.expensetracker.di.DatabaseModule]).
//  * Never call [create] directly in application code.
//  */
// @Database(
//     entities = [
//         TransactionEntity::class,
//         MerchantEntity::class,
//         CategoryEntity::class,
//     ],
//     version = 1,
//     exportSchema = true,
// )
// abstract class AppDatabase : RoomDatabase() {
//
//     abstract fun transactionDao(): RoomTransactionDao
//     abstract fun merchantDao(): RoomMerchantDao
//     abstract fun categoryDao(): RoomCategoryDao
//
//     companion object {
//         private const val DB_NAME = "expense_tracker.db"
//
//         fun create(context: Context, keyProvider: DatabaseKeyProvider): AppDatabase {
//             // Zero the passphrase after the SupportFactory copies it internally.
//             val passphrase = keyProvider.getDatabaseKey()
//             val factory = try {
//                 SupportFactory(passphrase)
//             } finally {
//                 passphrase.fill(0)
//             }
//
//             return Room.databaseBuilder(context, AppDatabase::class.java, DB_NAME)
//                 .openHelperFactory(factory)
//                 .addCallback(SeedCallback)
//                 .build()
//         }
//
//         /** Seeds category display metadata on first database creation. */
//         private val SeedCallback = object : RoomDatabase.Callback() {
//             override fun onCreate(db: SupportSQLiteDatabase) {
//                 CategoryEntity.seedData().forEach { category ->
//                     db.execSQL(
//                         "INSERT OR IGNORE INTO categories(id, display_name, icon_key, color_hex) VALUES (?,?,?,?)",
//                         arrayOf(category.id, category.displayName, category.iconKey, category.colorHex),
//                     )
//                 }
//             }
//         }
//     }
// }
