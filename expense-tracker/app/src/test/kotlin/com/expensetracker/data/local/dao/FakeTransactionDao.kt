package com.expensetracker.data.local.dao

import com.expensetracker.data.local.entity.TransactionEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.update

/**
 * In-memory [TransactionDao] for unit tests.
 *
 * State is backed by a [MutableStateFlow] so [observeAll] and [observeByCategory] emit
 * reactively on every [upsert] or [deleteById] call — no manual refresh needed.
 */
class FakeTransactionDao : TransactionDao {
    private val flow = MutableStateFlow<List<TransactionEntity>>(emptyList())
    private var nextId = 1L

    override fun observeAll(): Flow<List<TransactionEntity>> = flow.map { list -> list.sortedByDescending { it.timestampMillis } }

    override fun observeByCategory(category: String): Flow<List<TransactionEntity>> =
        flow.map { list ->
            list
                .filter { it.category == category }
                .sortedByDescending { it.timestampMillis }
        }

    override suspend fun findById(id: Long): TransactionEntity? = flow.value.firstOrNull { it.id == id }

    override suspend fun upsert(entity: TransactionEntity): Long {
        val id = if (entity.id == 0L) nextId++ else entity.id
        val record = entity.copy(id = id)
        flow.update { list ->
            val existing = list.indexOfFirst { it.id == id }
            if (existing >= 0) {
                list.toMutableList().also { it[existing] = record }
            } else {
                list + record
            }
        }
        return id
    }

    override suspend fun deleteById(id: Long) {
        flow.update { list -> list.filter { it.id != id } }
    }

    override suspend fun searchByDescription(query: String): List<TransactionEntity> =
        flow.value.filter { it.description.contains(query, ignoreCase = true) }
}
