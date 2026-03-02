package com.expensetracker.data.local.dao

import com.expensetracker.data.local.entity.CategoryEntity

// ANDROID-ONLY: import androidx.room.Dao

/**
 * Data access contract for [CategoryEntity].
 *
 * Category rows are seeded once at database creation (see [CategoryEntity.seedData]).
 * They are read-mostly; [upsertAll] is used only during seed and potential future migrations.
 */
interface CategoryDao {
    /** Returns all category rows. */
    suspend fun findAll(): List<CategoryEntity>

    /** Returns the category with the given [id] (a [com.expensetracker.domain.model.Category.name]), or `null`. */
    suspend fun findById(id: String): CategoryEntity?

    /**
     * Inserts or replaces all provided category rows.
     * Used at database creation to seed [CategoryEntity.seedData].
     */
    suspend fun upsertAll(entities: List<CategoryEntity>)
}
