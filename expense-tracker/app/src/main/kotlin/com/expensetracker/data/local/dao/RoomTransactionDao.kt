@file:Suppress("ktlint:standard:no-empty-file")

package com.expensetracker.data.local.dao

// ANDROID-ONLY — This file requires the Android Gradle plugin + Room.
// Uncomment imports and interface body when migrating.
//
// import androidx.room.Dao
// import androidx.room.Query
// import androidx.room.Upsert
// import com.expensetracker.data.local.entity.TransactionEntity
// import kotlinx.coroutines.flow.Flow
//
// /**
//  * Room implementation of [TransactionDao].
//  *
//  * Extending [TransactionDao] is the compile-time guarantee that every Room SQL query
//  * satisfies the plain-Kotlin interface used by [LocalExpenseRepository] and its tests.
//  *
//  * SQLCipher note: the database connection is encrypted via a [net.zetetic.database.sqlcipher.SupportFactory]
//  * configured in [AppDatabase]. No special DAO-level configuration is required.
//  */
// @Dao
// interface RoomTransactionDao : TransactionDao {
//
//     @Query("SELECT * FROM transactions ORDER BY timestamp_millis DESC")
//     override fun observeAll(): Flow<List<TransactionEntity>>
//
//     @Query("SELECT * FROM transactions WHERE category = :category ORDER BY timestamp_millis DESC")
//     override fun observeByCategory(category: String): Flow<List<TransactionEntity>>
//
//     @Query("SELECT * FROM transactions WHERE id = :id LIMIT 1")
//     override suspend fun findById(id: Long): TransactionEntity?
//
//     @Upsert
//     override suspend fun upsert(entity: TransactionEntity): Long
//
//     @Query("DELETE FROM transactions WHERE id = :id")
//     override suspend fun deleteById(id: Long)
//
//     @Query("""
//         SELECT * FROM transactions
//         WHERE description LIKE '%' || :query || '%'
//         ORDER BY timestamp_millis DESC
//     """)
//     override suspend fun searchByDescription(query: String): List<TransactionEntity>
// }
