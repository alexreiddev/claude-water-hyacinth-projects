package com.expensetracker.data.local.dao

import com.expensetracker.data.local.entity.TransactionEntity
import kotlinx.coroutines.flow.Flow

// ANDROID-ONLY: import androidx.room.Dao

/**
 * Data access contract for [TransactionEntity].
 *
 * Implementations on Android extend this interface via [RoomTransactionDao], which adds
 * Room `@Query` / `@Upsert` annotations while satisfying this interface at compile time.
 *
 * In tests, [com.expensetracker.data.local.dao.FakeTransactionDao] provides an in-memory
 * implementation backed by [kotlinx.coroutines.flow.MutableStateFlow].
 */
interface TransactionDao {
    /** Emits the full list of transactions ordered by timestamp descending, re-emitting on change. */
    fun observeAll(): Flow<List<TransactionEntity>>

    /** Emits transactions matching [category] (a [com.expensetracker.domain.model.Category.name]). */
    fun observeByCategory(category: String): Flow<List<TransactionEntity>>

    /** Returns the transaction with [id], or `null` if not found. */
    suspend fun findById(id: Long): TransactionEntity?

    /**
     * Inserts a new transaction or replaces an existing one with the same [TransactionEntity.id].
     * If [TransactionEntity.id] is 0, a new auto-generated id is assigned.
     *
     * @return the row id of the inserted/updated record.
     */
    suspend fun upsert(entity: TransactionEntity): Long

    /** Deletes the transaction with [id]. No-op if the id does not exist. */
    suspend fun deleteById(id: Long)

    /** Returns transactions whose [TransactionEntity.description] contains [query] (case-insensitive). */
    suspend fun searchByDescription(query: String): List<TransactionEntity>
}
