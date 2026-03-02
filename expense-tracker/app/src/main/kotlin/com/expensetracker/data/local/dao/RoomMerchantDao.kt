@file:Suppress("ktlint:standard:no-empty-file")

package com.expensetracker.data.local.dao

// ANDROID-ONLY — This file requires the Android Gradle plugin + Room.
// Uncomment imports and interface body when migrating.
//
// import androidx.room.Dao
// import androidx.room.Query
// import androidx.room.Upsert
// import com.expensetracker.data.local.entity.MerchantEntity
//
// /**
//  * Room implementation of [MerchantDao].
//  *
//  * Extending [MerchantDao] is the compile-time guarantee that the Room SQL queries
//  * satisfy the plain-Kotlin interface used by the ingestion module.
//  */
// @Dao
// interface RoomMerchantDao : MerchantDao {
//
//     @Query("SELECT * FROM merchants WHERE normalized_name = :normalizedName LIMIT 1")
//     override suspend fun findByNormalizedName(normalizedName: String): MerchantEntity?
//
//     @Query("SELECT * FROM merchants WHERE id = :id LIMIT 1")
//     override suspend fun findById(id: Long): MerchantEntity?
//
//     @Upsert
//     override suspend fun upsert(entity: MerchantEntity): Long
// }
