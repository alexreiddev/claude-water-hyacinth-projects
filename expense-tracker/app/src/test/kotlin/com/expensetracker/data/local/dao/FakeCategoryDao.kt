package com.expensetracker.data.local.dao

import com.expensetracker.data.local.entity.CategoryEntity

/**
 * In-memory [CategoryDao] for unit tests.
 */
class FakeCategoryDao : CategoryDao {
    private val store = mutableMapOf<String, CategoryEntity>()

    override suspend fun findAll(): List<CategoryEntity> = store.values.toList()

    override suspend fun findById(id: String): CategoryEntity? = store[id]

    override suspend fun upsertAll(entities: List<CategoryEntity>) {
        entities.forEach { store[it.id] = it }
    }
}
