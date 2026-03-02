package com.expensetracker.data.local

import com.expensetracker.data.local.dao.TransactionDao
import com.expensetracker.data.local.mapper.toDomain
import com.expensetracker.data.local.mapper.toEntity
import com.expensetracker.domain.model.Category
import com.expensetracker.domain.model.Expense
import com.expensetracker.domain.repository.ExpenseRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

/**
 * Room-backed implementation of [ExpenseRepository].
 *
 * All persistence is delegated to [TransactionDao]; mapping between the [TransactionEntity]
 * data-layer type and the [Expense] domain type is handled by [TransactionMapper].
 *
 * Merchant resolution (linking a transaction to a [com.expensetracker.data.local.entity.MerchantEntity])
 * is deferred to Module 2 (ingestion). For Module 1 all saves store a null [merchantId].
 *
 * ## Thread safety
 * Room (on Android) executes DAO suspend functions on a background dispatcher.
 * In JVM tests, the fake DAO runs on the test dispatcher provided by [kotlinx.coroutines.test.runTest].
 * No additional dispatcher switching is needed in this class.
 *
 * ## ANDROID-ONLY wiring (Hilt)
 * See [com.expensetracker.di.DatabaseModule] for how this class is provided as a singleton.
 */
class LocalExpenseRepository(
    private val transactionDao: TransactionDao,
) : ExpenseRepository {
    override fun getAll(): Flow<List<Expense>> =
        transactionDao
            .observeAll()
            .map { entities -> entities.map { it.toDomain() } }

    override fun getByCategory(category: Category): Flow<List<Expense>> =
        transactionDao
            .observeByCategory(category.name)
            .map { entities -> entities.map { it.toDomain() } }

    override suspend fun getById(id: Long): Expense? = transactionDao.findById(id)?.toDomain()

    override suspend fun save(expense: Expense): Long = transactionDao.upsert(expense.toEntity())

    override suspend fun delete(id: Long): Unit = transactionDao.deleteById(id)

    override suspend fun searchByDescription(query: String): List<Expense> =
        transactionDao
            .searchByDescription(query)
            .map { it.toDomain() }
}
