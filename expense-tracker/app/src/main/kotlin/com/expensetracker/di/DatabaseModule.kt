// ANDROID-ONLY Hilt wiring shown below.
// The object below this comment block is a plain-Kotlin factory for JVM/test use.
//
// ANDROID-ONLY (uncomment when migrating to Android + Hilt):
//
// package com.expensetracker.di
//
// import android.content.Context
// import com.expensetracker.data.local.LocalExpenseRepository
// import com.expensetracker.data.local.dao.CategoryDao
// import com.expensetracker.data.local.dao.MerchantDao
// import com.expensetracker.data.local.dao.TransactionDao
// import com.expensetracker.data.local.db.AppDatabase
// import com.expensetracker.domain.repository.ExpenseRepository
// import com.expensetracker.system.security.AndroidDatabaseKeyProvider
// import com.expensetracker.system.security.DatabaseKeyProvider
// import dagger.Module
// import dagger.Provides
// import dagger.hilt.InstallIn
// import dagger.hilt.android.qualifiers.ApplicationContext
// import dagger.hilt.components.SingletonComponent
// import javax.inject.Singleton
//
// @Module
// @InstallIn(SingletonComponent::class)
// object DatabaseModule {
//
//     @Provides
//     @Singleton
//     fun provideKeyProvider(): DatabaseKeyProvider = AndroidDatabaseKeyProvider()
//
//     @Provides
//     @Singleton
//     fun provideDatabase(
//         @ApplicationContext context: Context,
//         keyProvider: DatabaseKeyProvider,
//     ): AppDatabase = AppDatabase.create(context, keyProvider)
//
//     @Provides
//     fun provideTransactionDao(db: AppDatabase): TransactionDao = db.transactionDao()
//
//     @Provides
//     fun provideMerchantDao(db: AppDatabase): MerchantDao = db.merchantDao()
//
//     @Provides
//     fun provideCategoryDao(db: AppDatabase): CategoryDao = db.categoryDao()
//
//     @Provides
//     @Singleton
//     fun provideExpenseRepository(transactionDao: TransactionDao): ExpenseRepository =
//         LocalExpenseRepository(transactionDao)
// }

package com.expensetracker.di

import com.expensetracker.data.local.LocalExpenseRepository
import com.expensetracker.data.local.dao.TransactionDao
import com.expensetracker.domain.repository.ExpenseRepository

/**
 * Plain-Kotlin factory for JVM and test wiring.
 *
 * On Android, delete this object and use the Hilt `@Module` shown in the comment block above.
 */
object DatabaseModule {
    fun createExpenseRepository(transactionDao: TransactionDao): ExpenseRepository = LocalExpenseRepository(transactionDao)
}
