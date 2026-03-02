package com.expensetracker.data.local.dao

import com.expensetracker.data.local.entity.MerchantEntity

/**
 * In-memory [MerchantDao] for unit tests.
 */
class FakeMerchantDao : MerchantDao {
    private val store = mutableMapOf<Long, MerchantEntity>()
    private var nextId = 1L

    override suspend fun findByNormalizedName(normalizedName: String): MerchantEntity? =
        store.values.firstOrNull { it.normalizedName == normalizedName }

    override suspend fun findById(id: Long): MerchantEntity? = store[id]

    override suspend fun upsert(entity: MerchantEntity): Long {
        val id = if (entity.id == 0L) nextId++ else entity.id
        store[id] = entity.copy(id = id)
        return id
    }
}
