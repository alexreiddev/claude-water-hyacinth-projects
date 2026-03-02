package com.expensetracker.data.local.dao

import com.expensetracker.data.local.entity.MerchantEntity

// ANDROID-ONLY: import androidx.room.Dao

/**
 * Data access contract for [MerchantEntity].
 *
 * Populated by the ingestion module (Module 2). The storage layer only needs
 * look-up and upsert; deletion is not exposed (merchants are retained for history).
 */
interface MerchantDao {
    /**
     * Looks up a merchant by its [MerchantEntity.normalizedName] (lowercase-trimmed).
     * Returns `null` if not yet seen.
     */
    suspend fun findByNormalizedName(normalizedName: String): MerchantEntity?

    /** Returns the merchant with [id], or `null`. */
    suspend fun findById(id: Long): MerchantEntity?

    /**
     * Inserts or replaces the merchant record.
     *
     * @return the row id of the inserted/updated record.
     */
    suspend fun upsert(entity: MerchantEntity): Long
}
